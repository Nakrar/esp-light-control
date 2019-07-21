import logging
import math
import random
import time

from constants import ANIMATION_MAX_FPS, RGB_COUNT
from helpers import next_animation_frame, hsl_to_rgb, gradient

ANIMATIONS = []


frames = 0
last_time = 0


def animation_cycle():
    global ANIMATIONS
    global frames
    global last_time

    if ANIMATIONS:
        new_animations = None
        for animation in ANIMATIONS:
            if not next_animation_frame(animation):
                if new_animations is None:
                    new_animations = list(ANIMATIONS)
                new_animations.remove(animation)

        if new_animations is not None:
            ANIMATIONS = new_animations

        now_time = time.time()
        if now_time > last_time:
            logging.info('fps {}'.format(frames))
            last_time = now_time
            frames = 0
        frames += 1

        return True
    return False


def add_animation(animation):
    ANIMATIONS.append(animation)


def cleat_animations():
    ANIMATIONS.clear()


def pastel_breathe(strip, time_per_color=63, blend_in_time=3, breathe_time=20, s=0.8, l=0.8):
    # starts breathe animation, updates on yield
    sections = 6
    color_sections = 2

    if time_per_color < blend_in_time:
        raise ValueError(
            'time_per_color < blend_in_time: {} and {}'.format(time_per_color, blend_in_time))

    part = int(RGB_COUNT / sections)

    def _write_colors(new_color):

        # https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/neopixel.py
        strip._np.buf = b''.join(bytes((new_color[i][1], new_color[i][0], new_color[i][2]) * part)
                                 for i in range(sections))

        strip._np.write()

    def _fade_continuous(from_colors, to_colors, time):
        colors_n = len(from_colors)

        if len(to_colors) != colors_n:
            raise ValueError('len(from_colors) {} != len(to_colors) {}'.format(len(to_colors), colors_n))

        frames = int(ANIMATION_MAX_FPS * time + 0.5)
        current_colors = list(from_colors)

        for frame in range(frames):

            t = (frame + 1) / frames

            for i in range(colors_n):
                current_colors[i] = gradient(from_colors[i], to_colors[i], t)

            yield current_colors

    def breathe(colors):

        h_breathe_delta = 0.05
        s_breathe_delta = 0.1
        l_breathe_delta = 0.05

        colors_n = len(colors)
        current_colors = list(colors)

        while True:

            breathe_frames = int(breathe_time * ANIMATION_MAX_FPS + 0.5)

            for frame in range(breathe_frames):
                t = (frame + 1) / breathe_frames
                frame_t = (4 * math.pi) * t

                for i in range(colors_n):
                    h, s, l = colors[i]

                    h += h_breathe_delta * math.sin(frame_t + math.pi * i)
                    s += s_breathe_delta * math.sin(frame_t + math.pi * i + math.pi)
                    l += l_breathe_delta * math.sin(frame_t * 0.5 + math.pi * i)

                    h %= 1
                    s = min(max(0, s), 1)
                    l = min(max(0, l), 1)

                    current_colors[i] = hsl_to_rgb(h, s, l)

                yield current_colors

    def new_colors(hue_current, s, l, colors_n, sections_n):
        colors = [(hue_current / 360, s, l)] + [
            ((hue_current + random.randint(60, 300)) % 360 / 360, s, l)
            for _ in range(colors_n - 1)
        ]

        return [colors[int(i / (sections_n / colors_n))] for i in range(sections_n)]

    hue_current = random.randrange(360)

    frames_per_color = time_per_color * ANIMATION_MAX_FPS
    # update right after launch

    current_colors = [(0, 0, 0) for i in range(sections)]

    while True:
        # generate new colors if frames of current color exited
        hue_current = (hue_current + random.randint(60, 300)) % 360

        hsl_colors = new_colors(hue_current, s, l, colors_n=color_sections, sections_n=sections)

        # create blend_in animation
        to_colors = [hsl_to_rgb(*hsl_colors[i]) for i in range(sections)]
        animation = _fade_continuous(current_colors, to_colors, blend_in_time)

        for frame_counter in range(frames_per_color):

            if animation:
                try:
                    current_colors = next(animation)
                    _write_colors(current_colors)
                except StopIteration:
                    animation = None

            if animation is None:
                animation = breathe(hsl_colors)

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
    steps = int(time * ANIMATION_MAX_FPS + 0.5)

    for step in range(steps):
        t = (step + 1) / steps
        # easeOutCubic
        t1 = t - 1
        ease_k = t1 * t * t + 1

        strip.set_brightness(start + (delta * t * ease_k))
        yield
