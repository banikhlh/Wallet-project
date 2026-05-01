from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from core.security import create_access_token, get_current_user, decode_access_token, get_optional_current_user
from core.templates import templates
from core.rate_limit import LoginRateLimiter
from crud.user import UserCRUD
from schemas.user import UserCreate, UserResponse
from crud.transaction import TransactionCRUD
from dependencies import get_db
from database.database import Database
from tools.facts import generate_fact
from datetime import datetime

router = APIRouter(prefix="", tags=["views"])
login_limiter = LoginRateLimiter(max_attempts=5, lockout_minutes=15)

async def render_template(request: Request, name: str, context: dict = None) -> HTMLResponse:
    if context is None:
        context = {}
    context.setdefault("request", request)

    user = await get_optional_current_user(request)
    context["current_user"] = user

    template = templates.get_template(name)
    content = template.render(context)
    return HTMLResponse(content)


@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    token = request.cookies.get("access_token")
    if token:
        payload = decode_access_token(token)
        if payload:
            return RedirectResponse(url="/dashboard", status_code=303)
    return await render_template(request, "index.html")


@router.get("/register", response_class=HTMLResponse, name="show_registration_form")
async def show_registration_form(request: Request):
    return await render_template(request, "register.html", {
        "request": request,
        "form_data": {},
        "errors": {},
        "messages": {}
    })


@router.post("/register", name="handle_registration")
async def handle_registration(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Database = Depends(get_db)
):
    errors = {}
    form_data = {
        "username": username,
        "password": password,
        "confirm_password": confirm_password
    }
    
    if not username:
        errors["username"] = "Имя пользователя обязательно"
    if not password:
        errors["password"] = "Пароль обязателен"
    elif len(password) < 6:
        errors["password"] = "Пароль должен быть не менее 6 символов"
    if password != confirm_password:
        errors["confirm_password"] = "Пароли не совпадают"
        
    if not errors:
        user_crud = UserCRUD(db)
        existing = await user_crud.get_by_username(username)
        if existing:
            errors["username"] = "Пользователь с таким именем уже существует"
            
    if errors:
        return await render_template(request, "register.html", {
            "request": request,
            "form_data": form_data,
            "errors": errors,
            "messages": {}
        })
        
    try:
        user_crud = UserCRUD(db)
        await user_crud.create(UserCreate(username=username, password=password))
    except Exception as e:
        errors["general"] = f"Ошибка регистрации: {str(e)}"
        return await render_template(request, "register.html", {
            "form_data": form_data,
            "errors": errors,
            "messages": {}
        })
        
    return RedirectResponse(url="/login?registered=true", status_code=303)


@router.get("/login", response_class=HTMLResponse, name="show_login_form")
async def show_login_form(
    request: Request,
    registered: str = None,
    error: str = None
):
    return await render_template(request, "login.html", {
        "request": request,
        "registered": registered,
        "error": error,
        "form_data": {}
    })


@router.post("/login", name="handle_login")
async def handle_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Database = Depends(get_db)
):
    if login_limiter.is_blocked(username):
        return await render_template(request, "login.html", {
            "error": "Слишком много попыток. Попробуйте позже.",
            "form_data": {"username": username}
        })
    
    
    user_crud = UserCRUD(db)
    user = await user_crud.authenticate(username, password)

    if not user:
        return await render_template(request, "login.html", {
            "request": request,
            "error": "Неверное имя пользователя или пароль",
            "form_data": {"username": username}
        })
        
    login_limiter.reset_attempts(username)
    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=60 * 60 * 24
    )
    return response


@router.get("/logout", name="logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token", path='/')
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request,
                    current_user: UserResponse = Depends(get_current_user),
                    db: Database = Depends(get_db)):
    crud = TransactionCRUD(db)
    summary = await crud.get_stats_summary(current_user.id, "month")
    by_category = await crud.get_by_category(current_user.id, "month", "expense")
    by_category_income = await crud.get_by_category(current_user.id, "month", "income")
    fact = await generate_fact(db, current_user.id)
    rating_message = None

    return await render_template(request, "dashboard.html", {
        "summary": summary,
        "fact": fact,
        "rating_message": rating_message
    })
    
    
    
@router.get("/settings", response_class=HTMLResponse)
async def view_settings(request: Request,
                        current_user: UserResponse = Depends(get_current_user)):
    theme = request.cookies.get("theme", "light")
    return await render_template(request, "settings.html", {"theme": theme})

@router.post("/settings", name="handle_settings")
async def handle_settings(
    request: Request,
    action: str = Form(...),
    new_username: str = Form(None),
    current_password: str = Form(None),
    new_password: str = Form(None),
    confirm_new_password: str = Form(None),
    db: Database = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    user_crud = UserCRUD(db)
    error = None
    success = None

    if action == "change_username":
        if not new_username or new_username == current_user.username:
            error = "Имя не изменилось"
        else:
            existing = await user_crud.get_by_username(new_username)
            if existing:
                error = "Имя занято"
            else:
                await user_crud.update(current_user.id, username=new_username)
                response = RedirectResponse(url="/logout", status_code=303)
                return response

    elif action == "change_password":
        if not current_password or not new_password or not confirm_new_password:
            error = "Заполните все поля пароля"
        elif new_password != confirm_new_password:
            error = "Пароли не совпадают"
        else:
            authed = await user_crud.authenticate(current_user.username, current_password)
            if not authed:
                error = "Неверный текущий пароль"
            else:
                await user_crud.update(current_user.id, password=new_password)
                success = "Пароль изменён. Войдите заново."
                response = RedirectResponse(url="/logout", status_code=303)
                return response

    theme = request.cookies.get("theme", "light")
    return await render_template(request, "settings.html", {
        "error": error,
        "success": success,
        "theme": theme
    })