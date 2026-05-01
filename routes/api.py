# routes/api.py
from fastapi import APIRouter, Depends, Query, Form
from database.database import Database
from crud.transaction import TransactionCRUD
from core.security import get_current_user
from dependencies import get_db
from schemas.user import UserResponse

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/categories")
async def api_categories(type: str = Query(...), db: Database = Depends(get_db)):
    rows = await db.execute(
        "SELECT id, name, icon, color FROM categories WHERE type = ? ORDER BY name", (type,)
    )
    return rows

@router.post("/transactions", status_code=201)
async def api_create_transaction(
    category_id: int = Form(...),
    amount: float = Form(...),
    type: str = Form(...),
    description: str = Form(""),
    date: str = Form(""),
    current_user: UserResponse = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    crud = TransactionCRUD(db)
    date_val = date if date else None
    tid = await crud.create(current_user.id, category_id, amount, type, description, date_val)
    return {"id": tid, "message": "Транзакция добавлена"}

@router.get("/stats/summary")
async def api_summary(period: str = Query("month"), current_user: UserResponse = Depends(get_current_user), db: Database = Depends(get_db)):
    crud = TransactionCRUD(db)
    return await crud.get_stats_summary(current_user.id, period)

@router.get("/stats/by-category")
async def api_by_category(period: str = Query("month"), type: str = Query("expense"),
                          current_user: UserResponse = Depends(get_current_user), db: Database = Depends(get_db)):
    crud = TransactionCRUD(db)
    return await crud.get_by_category(current_user.id, period, type)

@router.get("/stats/trend")
async def api_trend(months: int = Query(6, ge=0, le=24), current_user: UserResponse = Depends(get_current_user), db: Database = Depends(get_db)):
    crud = TransactionCRUD(db)
    return await crud.get_monthly_trend(current_user.id, months)