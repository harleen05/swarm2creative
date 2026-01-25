def clamp(value, min_v, max_v):
    return max(min_v, min(max_v, value))


def confidence_ok(c):
    return c >= 0.35


def apply_delta(current, delta, confidence, min_v=None, max_v=None):
    if not confidence_ok(confidence):
        return current

    new = current + delta * confidence
    if min_v is not None and max_v is not None:
        new = clamp(new, min_v, max_v)
    return new