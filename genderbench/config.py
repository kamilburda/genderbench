import os

_default_env_values = {
    "GENDER_BENCH_LOG_DIR": "logs/",
}


def get_env_variable(name):
    default_value = _default_env_values.get(name, None)
    return os.getenv(name, default_value)
