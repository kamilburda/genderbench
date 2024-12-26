import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()


def get_env_variable(name, default=None, cast_type=None):
    value = os.getenv(name, default)
    if cast_type is not None:
        value = cast_type(value)
    return value


# Define configuration variables
LOG_DIR = get_env_variable("LOG_DIR", default="logs/")
