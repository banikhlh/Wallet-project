import pytest
from crud.transaction import TransactionCRUD
from crud.user import UserCRUD
from core.categories import CATEGORIES
from crud.user import UserCRUD
from schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_and_stats(override_get_db):
    db = override_get_db
    user_crud = UserCRUD(db)
    trans_crud = TransactionCRUD(db)

    user = await user_crud.create(UserCreate(username="dave", password="123456"))
    cat_rows = await db.execute("SELECT id FROM categories WHERE name='Продукты'")
    cat_id = cat_rows[0]["id"]

    await trans_crud.create(user.id, cat_id, 500, "expense", "еда")
    await trans_crud.create(user.id, cat_id, 300, "expense", "ещё еда")
    await trans_crud.create(user.id, cat_id, 2000, "income", "зарплата")

    summary = await trans_crud.get_stats_summary(user.id, "month")
    assert summary["expense"] == 800
    assert summary["income"] == 2000

    by_cat = await trans_crud.get_by_category(user.id, "month", "expense")
    assert len(by_cat) == 1
    assert by_cat[0]["name"] == "Продукты"
    assert by_cat[0]["total"] == 800

    trends = await trans_crud.get_monthly_trend(user.id, 1)
    assert len(trends) >= 1
    trends_all = await trans_crud.get_monthly_trend(user.id, 0)
    assert len(trends_all) >= 1