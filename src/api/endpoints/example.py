from fastapi import APIRouter, Depends

from src.database import (
    db_context,
    execute_sql,
    insert_model_into,
    get_model_by_key_value,
)
from src.database.types import DBContext
from src.types import Route, Example

router = APIRouter()


@router.post("/", response_model=int)
def post_example(example: Example, db: DBContext = Depends(db_context)):
    return insert_model_into(db, "test", "data", example)


@router.get("/")
def get_example(db: DBContext = Depends(db_context)):
    return execute_sql(db, """SELECT id FROM test.data""")


@router.get("/{example_id}")
def get_example_by_id(example_id: int, db: DBContext = Depends(db_context)):
    return get_model_by_key_value(db, "test", "data", Example, "id", example_id)


route = Route(router=router, prefix="/examples", tags=["Examples"])
