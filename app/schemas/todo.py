from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    priority: str

class TodoUpdate(BaseModel):
    title: str
    priority: str
    completed: bool

class TodoResponse(BaseModel):
    id: int
    title: str
    priority: str
    completed: bool

    model_config = {"from_attributes": True}
