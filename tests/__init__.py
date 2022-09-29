from dotenv import load_dotenv
from pathlib import Path

TESTS_ROOT_PATH = Path(__file__).parent
TESTS_DATA_PATH = TESTS_ROOT_PATH / 'data'

ENV_PATH = TESTS_DATA_PATH.parent / '.env'
load_dotenv(ENV_PATH)
