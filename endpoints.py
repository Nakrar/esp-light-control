import logging

import animations
import led
import routes
import strips


@routes.register('/')
@routes.register('/index')
@routes.register('/home')
def home_endpoint(request):
    return 'Hello user! Choices are: all, {}.'.format(', '.join(strips.STRIPS.keys()))


@routes.register('/strip/*')
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
        stps = strips.STRIPS.values()
    else:
        stps = (strip,)

    for strip in stps:
        # we want to achieve desired brightness in 0.6 second
        # for now there is 100fps
        step = (value - strip.get_brightness()) / 0.6 / 100
        anim = animations.brightness_animation(strip, strip.get_brightness(), value, step)
        animations.add_animation(anim)

    return '{} {}'.format(strip_name, value)


@routes.register('/strip/rgb/color')
def rgb_color_endpoint(request):
    strip = strips.STRIPS.get('rgb')
    if strip is None:
        return 'not found'

    value = request['args'].get('value')

    # for rgb "255,255,255" format
    try:
        color = tuple(int(x) for x in value.split(','))
    except (ValueError, TypeError):
        color = None

    # for hex "ffbb00" format
    if color is None and len(value) == 6:
        try:
            color = x = int(value, 16)
        except (ValueError, TypeError):
            color = None
        color = (color >> 16 & 255, color >> 8 & 255, color & 255)

    if color is None or not all(0 <= c <= 255 for c in color):
        return 'value must be "R,G,B" where r,g,b colors with from 0 to 255'

    logging.info('set color {}'.format(color))
    strip.set_color(color)

    return ''


@routes.register('/led')
def led_endpoint(request):
    value = request['args'].get('value')

    try:
        value = int(value)
    except (ValueError, TypeError):
        value = None

    if value is None and value != 1 and value != 0:
        return 'value must be 0 or 1'

    if value:
        led.on()
    else:
        led.off()


def register():
    # dummy for IDE
    pass
