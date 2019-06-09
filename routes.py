ROUTES = {
}


def register(path):
    def decorator(fn):
        if path in ROUTES:
            raise Exception('path already registered')
        ROUTES[path] = fn
        return fn

    return decorator
