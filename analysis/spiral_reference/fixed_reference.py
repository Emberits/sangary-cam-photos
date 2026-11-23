"""Experimental fixed-reference arithmetic; no image alignment or contour detector."""
import math


def measure(config, position, window, outer_width_px, *, registered=False,
            contour_valid=False, local_geometry_verified=False):
    if not registered:
        raise ValueError("registration_required")
    if not contour_valid:
        raise ValueError("invalid_contour")
    if position != "upper":
        raise ValueError("no_local_spiral_scale_for_this_conductor")
    if not local_geometry_verified:
        raise ValueError("local_geometry_not_verified")
    key = str(window)
    bare = config["bare_width_px"][position][key]
    spiral = config["green_width_px"][key]
    diameter = config["spiral_diameter_mm"]
    for value in (outer_width_px, bare, spiral, diameter):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError("invalid_dimension")
    scale = diameter / spiral
    delta = (outer_width_px - bare) * scale
    return {"position": position, "window": window, "mm_per_px": scale,
            "diameter_increase_mm": delta, "symmetric_equivalent_mm": delta / 2,
            "status": "below_reference" if delta < 0 else "experimental"}
