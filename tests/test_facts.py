import pytest
from tools.facts import generate_fact
from crud.user import UserCRUD
from crud.transaction import TransactionCRUD
from schemas.user import UserCreate


@pytest.mark.asyncio
async def test_fact_generation(override_get_db):
    db = override_get_db
    user_crud = UserCRUD(db)
    trans_crud = TransactionCRUD(db)

    user = await user_crud.create(UserCreate(username="factuser", password="123456"))
    cat_rows = await db.execute("SELECT id FROM categories WHERE name='Продукты'")
    cat_id = cat_rows[0]["id"]

    fact = await generate_fact(db, user.id)
    assert fact is None

    await trans_crud.create(user.id, cat_id, 5000, "expense", "трата")
    fact = await generate_fact(db, user.id)
    assert fact is not None
    isinstance(fact, str)

    await trans_crud.create(user.id, cat_id, 20000, "income", "доход")
    fact2 = await generate_fact(db, user.id)
    assert fact2 is not None
    assert not fact2.startswith("0 ")