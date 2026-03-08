"""Integration-like tests for user model and CRUD operations."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.models import User, UserRole
from app.routers.users import UserCreate, UserUpdate, ProfileUpdate


# Create SQLite in-memory database
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=TEST_ENGINE)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)


class TestUserModel:
    """Test User model can be created with all fields."""

    def test_create_user_with_all_fields(self, db_session):
        """Test creating user with all fields including timezone."""
        user = User(
            email="test@test.com",
            password_hash="hashed_password",
            name="Test User",
            role=UserRole.ADMIN,
            timezone="UTC",
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@test.com"
        assert user.name == "Test User"
        assert user.role == UserRole.ADMIN
        assert user.timezone == "UTC"
        assert user.is_active is True

    def test_create_user_with_minimal_fields(self, db_session):
        """Test creating user with minimal fields."""
        user = User(
            email="minimal@test.com",
            password_hash="hashed",
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.timezone is None  # Optional field

    def test_user_role_enum(self, db_session):
        """Test role enum values."""
        admin = User(email="admin@test.com", password_hash="x", role=UserRole.ADMIN)
        manager = User(email="manager@test.com", password_hash="x", role=UserRole.MANAGER)
        user = User(email="user@test.com", password_hash="x", role=UserRole.USER)
        
        db_session.add_all([admin, manager, user])
        db_session.commit()
        
        assert admin.role.value == "admin"
        assert manager.role.value == "manager"
        assert user.role.value == "user"


class TestUserSchemas:
    """Test Pydantic schemas for user operations."""

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        user = UserCreate(
            email="test@test.com",
            password="password123",
            name="Test",
            role="admin",
            timezone="UTC"
        )
        assert user.email == "test@test.com"
        assert user.role == "admin"
        assert user.timezone == "UTC"

    def test_user_create_default_role(self):
        """Test UserCreate has default role."""
        user = UserCreate(email="test@test.com", password="pass123")
        assert user.role == "user"  # Default
        assert user.timezone is None  # Optional

    def test_user_update_partial(self):
        """Test UserUpdate allows partial updates."""
        update = UserUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.role is None
        assert update.timezone is None

    def test_user_update_role_only(self):
        """Test updating only role."""
        update = UserUpdate(role="manager")
        assert update.role == "manager"

    def test_profile_update(self):
        """Test ProfileUpdate schema."""
        update = ProfileUpdate(name="My Name", timezone="America/New_York")
        assert update.name == "My Name"
        assert update.timezone == "America/New_York"

    def test_profile_update_partial(self):
        """Test ProfileUpdate partial updates."""
        update = ProfileUpdate(name="Name Only")
        assert update.name == "Name Only"
        assert update.timezone is None


class TestUserCRUDOperations:
    """Test database CRUD operations on User model."""

    def test_save_and_retrieve_user(self, db_session):
        """Test saving and retrieving user from DB."""
        user = User(
            email="crud@test.com",
            password_hash="hash",
            name="CRUD Test",
            role=UserRole.USER,
            timezone="Europe/London"
        )
        db_session.add(user)
        db_session.commit()
        
        # Retrieve
        retrieved = db_session.query(User).filter(User.email == "crud@test.com").first()
        assert retrieved is not None
        assert retrieved.name == "CRUD Test"
        assert retrieved.timezone == "Europe/London"

    def test_update_user_in_db(self, db_session):
        """Test updating user in database."""
        user = User(email="update@test.com", password_hash="x", role=UserRole.USER)
        db_session.add(user)
        db_session.commit()
        
        # Update
        user.name = "Updated Name"
        user.role = UserRole.MANAGER
        user.timezone = "Asia/Tokyo"
        db_session.commit()
        
        # Verify
        retrieved = db_session.query(User).filter(User.email == "update@test.com").first()
        assert retrieved.name == "Updated Name"
        assert retrieved.role == UserRole.MANAGER
        assert retrieved.timezone == "Asia/Tokyo"

    def test_delete_user_from_db(self, db_session):
        """Test deleting user from database."""
        user = User(email="delete@test.com", password_hash="x", role=UserRole.USER)
        db_session.add(user)
        db_session.commit()
        
        user_id = user.id
        
        # Delete
        db_session.delete(user)
        db_session.commit()
        
        # Verify
        retrieved = db_session.query(User).filter(User.id == user_id).first()
        assert retrieved is None

    def test_query_users_by_role(self, db_session):
        """Test querying users by role."""
        users = [
            User(email="a@test.com", password_hash="x", role=UserRole.ADMIN),
            User(email="b@test.com", password_hash="x", role=UserRole.ADMIN),
            User(email="c@test.com", password_hash="x", role=UserRole.USER),
        ]
        db_session.add_all(users)
        db_session.commit()
        
        admins = db_session.query(User).filter(User.role == UserRole.ADMIN).all()
        assert len(admins) == 2

    def test_user_with_null_timezone(self, db_session):
        """Test user with null timezone."""
        user = User(email="notz@test.com", password_hash="x", role=UserRole.USER)
        db_session.add(user)
        db_session.commit()
        
        assert user.timezone is None
