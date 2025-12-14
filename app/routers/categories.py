from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.dependencies import get_current_user
from app.repositories.categories import SqlAlchemyCategoryRepository
from app.repositories.habits import SqlAlchemyHabitRepository
from app.schemas import CategoryCreate, CategoryUpdate, CategoryOut
from app.services.categories import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    categories_repo = SqlAlchemyCategoryRepository(db)
    habits_repo = SqlAlchemyHabitRepository(db)
    return CategoryService(categories_repo, habits_repo)


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    category: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
    current_user: int = Depends(get_current_user),
):
    try:
        created_category = service.create(current_user, category.name, category.color)
        return created_category
    except ValueError as e:
        if str(e) == "name_exists":
            raise HTTPException(
                status_code=409, detail="Category name already exists"
            ) from e
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=List[CategoryOut])
def list_categories(
    service: CategoryService = Depends(get_category_service),
    current_user: int = Depends(get_current_user),
):
    return service.list_by_user(current_user)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
    current_user: int = Depends(get_current_user),
):
    category = service.get(category_id, current_user)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
    current_user: int = Depends(get_current_user),
):
    try:
        updated_category = service.update(category_id, current_user, category.name, category.color)
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated_category
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Category not found") from e
    except ValueError as e:
        if str(e) == "name_exists":
            raise HTTPException(
                status_code=409, detail="Category name already exists"
            ) from e
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
    current_user: int = Depends(get_current_user),
):
    try:
        service.delete(category_id, current_user)
        return {"ok": True}
    except LookupError as e:
        raise HTTPException(status_code=404, detail="Category not found") from e


@router.post("/{category_id}/habits/{habit_id}")
def add_habit_to_category(
    category_id: int,
    habit_id: int,
    service: CategoryService = Depends(get_category_service),
    current_user: int = Depends(get_current_user),
):
    try:
        service.add_habit_to_category(habit_id, category_id, current_user)
        return {"ok": True}
    except LookupError as e:
        error_msg = str(e)
        if error_msg == "category_not_found":
            raise HTTPException(status_code=404, detail="Category not found") from e
        elif error_msg == "habit_not_found":
            raise HTTPException(status_code=404, detail="Habit not found") from e
        raise HTTPException(status_code=404, detail="Not found") from e


@router.delete("/{category_id}/habits/{habit_id}")
def remove_habit_from_category(
    category_id: int,
    habit_id: int,
    service: CategoryService = Depends(get_category_service),
    current_user: int = Depends(get_current_user),
):
    try:
        service.remove_habit_from_category(habit_id, category_id, current_user)
        return {"ok": True}
    except LookupError as e:
        error_msg = str(e)
        if error_msg == "category_not_found":
            raise HTTPException(status_code=404, detail="Category not found") from e
        elif error_msg == "habit_not_found":
            raise HTTPException(status_code=404, detail="Habit not found") from e
        raise HTTPException(status_code=404, detail="Not found") from e
