from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean
from app.core.db_config import Base
from app.schemas.common_schema import UserRoleEnum
from sqlalchemy import Enum

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(Enum(UserRoleEnum), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)

    def __repr__(self):
        return f"{self.username}-{self.email}-{self.role}-{self.is_active}"