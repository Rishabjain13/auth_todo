from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import date

class TodoCreate(BaseModel):
    title: str
    priority: Literal["High", "Medium", "Low"]
    due_date: date = Field(default_factory=date.today)

class TodoUpdate(BaseModel):
    title: str
    priority: Literal["High", "Medium", "Low"]
    completed: bool
    due_date: Optional[date] = None

class TemplateCreate(BaseModel):
    name: str
    title: str
    priority: str
    
class TodoResponse(BaseModel):
    id: int
    title: str
    priority: str
    completed: bool

    model_config = {"from_attributes": True}
