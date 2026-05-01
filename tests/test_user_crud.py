import pytest
from crud.user import UserCRUD
from schemas.user import UserCreate
from database.database import Database
from core.security import hash_password


@pytest.mark.asyncio
async def test_create_and_get_user(override_get_db):
    db = override_get_db
    crud = UserCRUD(db)
    user = await crud.create(UserCreate(username="alice", password="123456"))
    assert user.id is not None
    assert user.username == "alice"
    assert user.is_active is True

    fetched = await crud.get_by_id(user.id)
    assert fetched.username == "alice"

    by_name = await crud.get_by_username("alice")
    assert by_name.id == user.id


@pytest.mark.asyncio
async def test_authenticate_user(override_get_db):
    db = override_get_db
    crud = UserCRUD(db)
    await crud.create(UserCreate(username="bob", password="qwerty"))
    user = await crud.authenticate("bob", "qwerty")
    assert user is not None
    assert user.username == "bob"
    assert await crud.authenticate("bob", "wrong") is None
    assert await crud.authenticate("nobody", "123") is None


@pytest.mark.asyncio
async def test_update_user(override_get_db):
    db = override_get_db
    crud = UserCRUD(db)
    user = await crud.create(UserCreate(username="charlie", password="oldpass"))
    updated = await crud.update(user.id, username="charlie_new", password="newpass")
    assert updated.username == "charlie_new"
    authed = await crud.authenticate("charlie_new", "newpass")
    assert authed is not None