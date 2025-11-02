import random
from typing import List, Dict, Optional
from enum import IntEnum

from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastapi import HTTPException


class Priority(IntEnum):
    """Defines priority levels for a to-do item, mapped to integer values for easy comparison and sorting."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class TodoBase(BaseModel):
    """Shared base model for to-do items, including name, description, and priority level."""
    
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Short title or label for the to-do item."
    )
    
    description: str = Field(
        ...,
        min_length=5,
        max_length=512,
        description="Detailed explanation of what the to-do item involves."
    )
    
    priority: Priority = Field(
        default=Priority.LOW,
        description="Indicates how urgent or important the to-do item is."
    )


class TodoCreate(TodoBase):
    """Model used when creating a new to-do item. Inherits all fields from TodoBase."""
    pass


class TodoUpdate(BaseModel):
    """Model used for updating an existing to-do item. All fields are optional to allow partial updates."""
    
    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Updated title or label for the to-do item."
    )
    
    description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=512,
        description="Updated details about the to-do item."
    )
    
    priority: Optional[Priority] = Field(
        None,
        description="Updated urgency level of the to-do item."
    )


class Todo(TodoBase):
    todo_id : int = Field(
        ...,
        description="Unique identifier of the to-do item."
    )


# generate 10 random Todos.
all_todos = [
    Todo(
        todo_id=i,
        name=f"todo{i}",
        description=f"description{i}",
        priority=random.choice(list(Priority))
    )
    for i in range(10)
]

api = FastAPI()

@api.get("/todos", response_model=List[Todo])
def todos(first_n : int = None) -> List[Todo]:    
    """Return all todos or return the first n todos."""
    if first_n is not None:
        if first_n < 0:
            raise HTTPException(status_code=400, detail="Index must be a positive number.")
        return all_todos[:first_n]    
    return all_todos

@api.get("/todo/{todo_id}", response_model=Todo)
def get_todo(todo_id : int) -> Todo:
    """Return a specific id or raise a HTTPException error if todo is non-existent"""
    for todo in all_todos:
        if todo.todo_id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found.")

@api.post("/todos/", response_model=Todo)
def create_todo(todo : TodoCreate) -> Todo:
    """Create a new todo."""
    new_id = max((t.todo_id for t in all_todos), default=-1)+1
    new_todo = Todo(todo_id = new_id, **todo.model_dump())
    all_todos.append(new_todo)
    return new_todo

@api.patch("/todo/{todo_id}/", response_model=Todo)
def update_todo(todo_id : int, updated_todo : TodoUpdate ) -> Todo:
    """Update the contents of a existing todo."""
    for todo in all_todos:
        if todo.todo_id == todo_id:
            # safe update to avoid 'errasing' data.
            if updated_todo.name is not None:
                todo.name = updated_todo.name
            if updated_todo.description is not None:
                todo.description = updated_todo.description
            if updated_todo.priority is not None:
                todo.priority = updated_todo.priority
            return todo
    raise HTTPException(status_code=404, detail='Todo not found')

@api.delete("/todo/{todo_id}/", response_model=Todo)
def delete_todo(todo_id : int) -> Todo:
    for index, todo in enumerate(all_todos):
        if todo.todo_id == todo_id:
            deleted_todo = all_todos.pop(index)
            return deleted_todo
    raise HTTPException(status_code=404, detail="Todo not found.")