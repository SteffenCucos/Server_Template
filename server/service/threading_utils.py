from threading import get_native_id


def get_current_pid() -> int:
    return get_native_id()
