from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.database.base import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    is_deleted = Column(Boolean, default=False)
    due_date = Column(Date, nullable=True)
