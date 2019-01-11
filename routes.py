ROUTES = {
}


def register(path):
    def decorator(fn):
        if path in ROUTES:
            print('path already registered')
            return
        ROUTES[path] = fn
        return fn

    return decorator
