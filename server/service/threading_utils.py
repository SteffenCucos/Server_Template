from threading import Thread


def run_task(task, arguments=()):
    print(arguments)
    Thread(target=task, args=arguments).start()
