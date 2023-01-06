from threading import Thread, get_native_id


def get_current_pid():
    return get_native_id()

def run_task(task, arguments=()):
    print(arguments)
    Thread(target=task, args=arguments).start()
