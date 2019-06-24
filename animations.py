import logging
import math
import random
import gc

import strips
from constants import ANIMATION_FPS, RGB_COUNT
from helpers import next_animation_frame, hsl_to_rgb, gradient

ANIMATIONS = []


def animation_cycle():
    print('animation_cycle')

    global ANIMATIONS

    if ANIMATIONS:
        new_animations = None
        for animation in ANIMATIONS:
            if not next_animation_frame(animation):
                if new_animations is None:
                    new_animations = list(ANIMATIONS)
                new_animations.remove(animation)

        if new_animations is not None:
            ANIMATIONS = new_animations

        rgb_strip = strips.STRIPS.get('rgb')
        if rgb_strip:
            rgb_strip.write()

        return True
    return False


def add_animation(animation):
    ANIMATIONS.append(animation)


def cleat_animations():
    ANIMATIONS.clear()


def fade_continuous(strip, to_color, time):
    # to_color is list of colors for each pixel to blend in
    # speed is 0 to 1
    frames = int(ANIMATION_FPS * time + 0.5)
    colors = [strip[i] for i in range(RGB_COUNT)]

    for frame in range(frames):
        print('fade')

        t = (frame + 1) / frames

        for i in range(RGB_COUNT):
            strip[i] = gradient(colors[i], to_color[i], t)

        yield


def pastel_breathe(strip, sections=2, time_per_color=100, blend_in_time=3, breathe_time=10, s=0.8, l=0.7):
    # starts breathe animation, updates on yield
    hue_current = random.randrange(360)
    # colors = [hsl_to_rgb(hue_current / 360, 0.7, 0.8)] + [
    #     hsl_to_rgb((hue_current + random.randint(60, 300)) % 360 / 360, 0.7, 0.8)
    #     for x in range(sections - 1)]

    animation = None

    h_breathe_delta = 0.1
    s_breathe_delta = 0.05
    l_breathe_delta = 0.05

    frames_per_color = time_per_color * ANIMATION_FPS
    # update right after launch
    frame_counter = frames_per_color

    if time_per_color < blend_in_time:
        raise ValueError(
            'time_per_color < blend_in_time: {} and {}'.format(time_per_color, blend_in_time))

    while True:
        print('pastel')

        # generate new colors if frames of current color exited
        if frame_counter == frames_per_color:
            frame_counter = 0
            hue_current = (hue_current + random.randint(60, 300)) % 360
            colors = [(hue_current / 360, s, l)] + [
                ((hue_current + random.randint(60, 300)) % 360 / 360, s, l)
                for _ in range(sections - 1)]

            h_t = random.random() * 3.14
            s_t = random.random() * 3.14
            l_t = random.random() * 3.14

            # create blend_in animation
            animation_colors = [hsl_to_rgb(*colors[int(i / (RGB_COUNT / sections))])
                                for i in range(RGB_COUNT)]
            animation = fade_continuous(strip, animation_colors, blend_in_time)
            gc.collect()

        # blend in colors, if animation is not over yet
        if animation:
            if not next_animation_frame(animation):
                animation = None
        else:
            # create breathe animation
            frame_t = math.sin(frame_counter / (ANIMATION_FPS * breathe_time))
            for i in range(RGB_COUNT):
                h, s, l = colors[int(i / (RGB_COUNT / sections))]

                t = (i / RGB_COUNT)
                h += h_breathe_delta * (math.cos(t * 3.14 + h_t) * frame_t)
                s += s_breathe_delta * (math.cos(t * 3 * 3.14 + s_t) * frame_t)
                l += l_breathe_delta * (math.cos(t * 2 * 3.14 + l_t) * frame_t)

                h %= 1
                s = min(max(0, s), 1)
                l = min(max(0, l), 1)

                strip[i] = hsl_to_rgb(h, s, l)

        frame_counter += 1

        yield


def brightness_animation(strip, start, end, time):
    # speed is 0 to 1
    if start == end:
        strip.set_brightness(end)
        return

    if not 0 <= start <= 100 or \
            not 0 <= end <= 100:
        logging.info("#brightness_animation: start {}, end {}, time {}".format(start, end, time))
        return

    delta = end - start
    steps = int(time * ANIMATION_FPS + 0.5)

    for step in range(steps):
        print('brightness_animation')
        t = (step + 1) / steps
        # easeOutCubic
        t1 = t - 1
        ease_k = t1 * t * t + 1

        strip.set_brightness(start + (delta * t * ease_k))
        yield
