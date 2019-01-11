from routes import register


@register('/')
def home_endpoint(request):
    return "Hello user!"

