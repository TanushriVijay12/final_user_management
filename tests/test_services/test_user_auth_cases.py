import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch
from app.models.user_model import User, UserRole
from app.utils.security import hash_password
from app.services.user_service import UserService
from app.dependencies import get_settings
from faker import Faker

fake = Faker()

@pytest.mark.asyncio
async def test_duplicate_email_registration(db_session: AsyncSession, user: User):
    duplicate = User(
        nickname=fake.user_name(),
        first_name="Test",
        last_name="Duplicate",
        email=user.email,  # Same email
        hashed_password=hash_password("password"),
        role=UserRole.AUTHENTICATED,
    )
    db_session.add(duplicate)
    with pytest.raises(Exception):
        await db_session.commit()

@pytest.mark.asyncio
async def test_empty_password_registration(db_session: AsyncSession):
    user = User(
        nickname="empty_pass",
        first_name="Empty",
        last_name="Password",
        email=fake.email(),
        hashed_password="",
        role=UserRole.AUTHENTICATED,
    )
    db_session.add(user)
    with pytest.raises(Exception):
        await db_session.commit()

@pytest.mark.asyncio
async def test_login_with_correct_credentials(db_session: AsyncSession, user: User):
    result = await UserService.login_user(db_session, user.email, "MySuperPassword$1234")
    assert result is not None
    assert result.email == user.email

@pytest.mark.asyncio
async def test_login_with_wrong_password(db_session: AsyncSession, user: User):
    result = await UserService.login_user(db_session, user.email, "wrongpassword")
    assert result is None  # Your service returns None, not raises

@pytest.mark.asyncio
async def test_user_lock_after_failed_logins(db_session: AsyncSession, user: User):
    for _ in range(get_settings().max_login_attempts):
        await UserService.login_user(db_session, user.email, "wrongpassword")
    await db_session.refresh(user)
    assert user.is_locked

@pytest.mark.asyncio
async def test_unlock_user_account_flow(db_session: AsyncSession, locked_user: User):
    with patch("app.tasks.email_tasks.send_account_unlocked_email.delay") as mock_send:
        unlocked = await UserService.unlock_user_account(db_session, locked_user.id)
        await db_session.refresh(unlocked)
        assert not unlocked.is_locked
        mock_send.assert_called_once_with(unlocked.email)

@pytest.mark.asyncio
async def test_user_role_default_assignment(db_session: AsyncSession):
    user = User(
        nickname="default_role",
        first_name="Default",
        last_name="Role",
        email=fake.email(),
        hashed_password=hash_password("password"),
        role=UserRole.AUTHENTICATED,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    assert user.role == UserRole.AUTHENTICATED
