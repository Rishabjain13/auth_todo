from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.base import Base

class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=frozenset)
