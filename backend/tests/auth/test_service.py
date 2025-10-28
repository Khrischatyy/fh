"""
Tests for authentication service.
"""
import pytest
from src.auth.service import auth_service
from src.auth.schemas import UserRegister
from src.auth.models import UserRole


@pytest.mark.asyncio
async def test_hash_password():
    """Test password hashing."""
    password = "testpassword123"
    hashed = auth_service.hash_password(password)
    assert hashed != password
    assert auth_service.verify_password(password, hashed)


@pytest.mark.asyncio
async def test_register_user(db_session):
    """Test user registration."""
    user_data = UserRegister(
        email="newuser@example.com",
        password="password123",
        password_confirmation="password123",
        firstname="New",
        lastname="User",
    )

    user = await auth_service.register_user(db_session, user_data)

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.firstname == "New"
    assert user.lastname == "User"
    assert user.role == UserRole.USER
    assert user.is_active is True
    assert user.is_verified is False
    assert user.password_hash is not None


@pytest.mark.asyncio
async def test_authenticate_user(db_session, test_user):
    """Test user authentication."""
    # Set known password
    test_user.password_hash = auth_service.hash_password("testpass123")
    await db_session.commit()

    # Authenticate with correct credentials
    user = await auth_service.authenticate_user(
        db_session, "test@example.com", "testpass123"
    )
    assert user is not None
    assert user.email == "test@example.com"

    # Authenticate with wrong password
    user = await auth_service.authenticate_user(
        db_session, "test@example.com", "wrongpassword"
    )
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_email(db_session, test_user):
    """Test getting user by email."""
    user = await auth_service.get_user_by_email(db_session, "test@example.com")
    assert user is not None
    assert user.email == "test@example.com"

    user = await auth_service.get_user_by_email(db_session, "nonexistent@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_create_access_token():
    """Test JWT token creation."""
    token = auth_service.create_access_token(data={"sub": 1})
    assert token is not None
    assert isinstance(token, str)

    # Decode token
    payload = auth_service.decode_access_token(token)
    assert payload["sub"] == 1
