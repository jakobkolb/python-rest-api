import dotenv

from src.database import db_test_context

try:
    dotenv.load_dotenv()
except Exception as e:
    print(e)

__all__ = ["db_test_context"]
