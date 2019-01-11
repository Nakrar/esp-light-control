import routes
import strips


@routes.register('/')
def home_endpoint(request):
    return 'Hello user! Choices are: ceil, wall, rgb, all.'


@routes.register('/strip/ceil')
@routes.register('/strip/wall')
@routes.register('/strip/rgb')
@routes.register('/strip/all')
def strip_endpoint(request):
    strip_name = request['path'].split('/')[-1]

    strip = strips.STRIPS.get(strip_name)
    if strip is None and strip_name != 'all':
        return 'not found'

    value = request['args'].get('value')

    try:
        value = int(value)
    except (ValueError, TypeError):
        value = None

    if value is None or not (0 <= value <= 100):
        return 'must be True: 0 <= value <= 100'

    if strip_name == 'all':
        for strip in strips.STRIPS:
            strips.set_brightness(strip, value)
    else:
        strips.set_brightness(strip, value)

    return '{} {}'.format(strip_name, value)
