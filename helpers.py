

def rgb_to_hsl(r, g, b):
    # https://gist.github.com/mathebox/e0805f72e7db3269ec22

    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, l = ((high + low) / 2,) * 3

    if high == low:
        h = 0.0
        s = 0.0
    else:
        d = high - low
        s = d / (2 - high - low) if low > 0.5 else d / (high + low)
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s, l


def _hue_to_rgb(p, q, t):
    # https://stackoverflow.com/a/9493060/6513203
    if t < 0:
        t += 1
    if t > 1:
        t -= 1
    if t < 0.16666:
        return p + (q - p) * 6 * t
    if t < 0.5:
        return q
    if t < 0.66666:
        return p + (q - p) * (2 / 3 - t) * 6
    return p


def hsl_to_rgb(h, s, l):
    # https://stackoverflow.com/a/9493060/6513203
    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = _hue_to_rgb(p, q, h + 0.33333)
        g = _hue_to_rgb(p, q, h)
        b = _hue_to_rgb(p, q, h - 0.33333)

    return int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5)


def next_animation_frame(animation):
    try:
        next(animation)
    except StopIteration:
        return False
    return True


def bezier_gradient(c0, c1, cp, t):
    # gradient from c0 to c1 through c2

    # set bezier point for result curve to go through c2
    cB = c0
    # cB = tuple(
    #     cp[x] * 2 - (c0[x] + c1[x]) / 2
    #     for x in range(3))

    # find point in bezier point
    out = tuple(
        (1 - t) ** 2 * c0[x] + (1 - t) * 2 * t * cB[x] + t * t * c1[x]
        for x in range(3))

    if any(int(x) < 0 or int(x) > 255 for x in out):
        raise ValueError

    return out


def get_curve_base_point(a, b):
    # finds middle of H from HSV repr of "a" and "b", returns RGB representation of middle_h
    h0, s0, l0 = rgb_to_hsl(*(x / 255 for x in a))
    h1, s1, l1 = rgb_to_hsl(*(x / 255 for x in b))

    if h0 < h1:
        h0, h1 = h1, h0

    zero_corr = 0
    if h0 - h1 > 180:
        # if 0-point across mid h0 - h1
        zero_corr = h1

        h1 = 360
        h0 -= zero_corr

    res_hvs = hsl_to_rgb(
        ((h0 + h1) / 2) + zero_corr,
        (s0 + s1) / 2,
        (l0 + l1) / 2
    )

    return tuple(x * 255 for x in res_hvs)


def gradient(c0, c1, t):
    bezier_base = get_curve_base_point(c0, c1)
    gradient_color = bezier_gradient(c0, c1, bezier_base, t)
    return tuple(int(x) for x in gradient_color)
