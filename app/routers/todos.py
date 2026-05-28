from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SubTask, Todo
from app.schemas import (
    SubTaskCreate,
    SubTaskResponse,
    SubTaskUpdate,
    TodoCreate,
    TodoResponse,
    TodoUpdate,
)

router = APIRouter(prefix="/todos", tags=["todos"])


def _get_todo_or_404(todo_id: int, db: Session) -> Todo:
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


def _get_subtask_or_404(todo_id: int, subtask_id: int, db: Session) -> SubTask:
    subtask = (
        db.query(SubTask)
        .filter(SubTask.todo_id == todo_id, SubTask.id == subtask_id)
        .first()
    )
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask


@router.get("/", response_model=list[TodoResponse])
def list_todos(
    completed: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Todo)
    if completed is not None:
        query = query.filter(Todo.completed == completed)
    return query.all()


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    return _get_todo_or_404(todo_id=todo_id, db=db)


@router.post("/", response_model=TodoResponse, status_code=201)
def create_todo(todo_data: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(**todo_data.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_data: TodoUpdate, db: Session = Depends(get_db)):
    todo = _get_todo_or_404(todo_id=todo_id, db=db)

    update_fields = todo_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(todo, field, value)

    todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = _get_todo_or_404(todo_id=todo_id, db=db)
    db.delete(todo)
    db.commit()


@router.get("/{todo_id}/subtasks/", response_model=list[SubTaskResponse])
def list_subtasks(
    todo_id: int,
    completed: bool | None = None,
    db: Session = Depends(get_db),
):
    _get_todo_or_404(todo_id=todo_id, db=db)
    query = db.query(SubTask).filter(SubTask.todo_id == todo_id)
    if completed is not None:
        query = query.filter(SubTask.completed == completed)
    return query.all()


@router.get("/{todo_id}/subtasks/{subtask_id}", response_model=SubTaskResponse)
def get_subtask(todo_id: int, subtask_id: int, db: Session = Depends(get_db)):
    _get_todo_or_404(todo_id=todo_id, db=db)
    return _get_subtask_or_404(todo_id=todo_id, subtask_id=subtask_id, db=db)


@router.post("/{todo_id}/subtasks/", response_model=SubTaskResponse, status_code=201)
def create_subtask(todo_id: int, subtask_data: SubTaskCreate, db: Session = Depends(get_db)):
    _get_todo_or_404(todo_id=todo_id, db=db)
    subtask = SubTask(todo_id=todo_id, **subtask_data.model_dump())
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask


@router.put("/{todo_id}/subtasks/{subtask_id}", response_model=SubTaskResponse)
def update_subtask(
    todo_id: int,
    subtask_id: int,
    subtask_data: SubTaskUpdate,
    db: Session = Depends(get_db),
):
    _get_todo_or_404(todo_id=todo_id, db=db)
    subtask = _get_subtask_or_404(todo_id=todo_id, subtask_id=subtask_id, db=db)

    update_fields = subtask_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(subtask, field, value)

    subtask.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(subtask)
    return subtask


@router.delete("/{todo_id}/subtasks/{subtask_id}", status_code=204)
def delete_subtask(todo_id: int, subtask_id: int, db: Session = Depends(get_db)):
    _get_todo_or_404(todo_id=todo_id, db=db)
    subtask = _get_subtask_or_404(todo_id=todo_id, subtask_id=subtask_id, db=db)
    db.delete(subtask)
    db.commit()
