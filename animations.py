import logging
import math

ANIMATIONS = []


def next_animation_frame(animation):
    try:
        next(animation)
    except StopIteration:
        return False
    return True


def animation_cycle():
    global ANIMATIONS
    ANIMATIONS = [a for a in ANIMATIONS if next_animation_frame(a)]
    if ANIMATIONS:
        return True
    return False


def add_animation(animation):
    ANIMATIONS.append(animation)


def brightness_animation(target_strip, start, end, speed):
    # speed is 0 to 1
    if start == end:
        target_strip.set_brightness(end)
        return

    if speed == 0 \
            or not 0 <= start <= 100 \
            or not 0 <= end <= 100 \
            or (start > end and speed > 0) \
            or (start < end and speed < 0):
        logging.info("#call of brightness_animation with: start {}, end {}, speed {}".format(start, end, speed))
        return

    steps = math.ceil(abs((start - end) / speed))

    for step in range(steps):
        target_strip.set_brightness(start + speed * step)
        yield

    target_strip.set_brightness(end)
