import math
from typing import List, Optional, Tuple

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import substring as shapely_substring
import rasterio
from pyproj import Transformer


def densify_linestring(line: LineString, step_m: float) -> List[Point]:
    """Return points sampled every step_m along the LineString (including end).

    - Assumes line is in a metric CRS.
    - Returns at least two points (start and end) if length > 0.
    """
    if not isinstance(line, LineString):
        raise TypeError("Expected LineString geometry")
    length = line.length
    if length <= 0:
        coords = list(line.coords)
        if len(coords) == 0:
            return []
        if len(coords) == 1:
            return [Point(coords[0]), Point(coords[0])]
        return [Point(coords[0]), Point(coords[-1])]
    dists = np.arange(0.0, max(0.0, length), max(step_m, 1e-6))
    if len(dists) == 0 or dists[-1] < length:
        dists = np.append(dists, length)
    return [line.interpolate(float(d)) for d in dists]


def _triangle_area_doubled(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> float:
    return abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax))


def compute_segment_radii(points: List[Point]) -> List[Optional[float]]:
    """Compute curvature radius for each segment using triplets of points.

    - Returns list of length (len(points)-1), each entry is the radius assigned to the segment [i,i+1].
    - For first and last segments, where a full triplet isn't available, returns None.
    - If points are nearly colinear, returns None for corresponding segments.
    """
    n = len(points)
    if n < 3:
        return [None for _ in range(max(0, n - 1))]
    xs = np.array([p.x for p in points], dtype=float)
    ys = np.array([p.y for p in points], dtype=float)
    radii: List[Optional[float]] = []
    for i in range(n - 1):
        if i == 0 or i == n - 2:
            radii.append(None)
            continue
        ax, ay = xs[i - 1], ys[i - 1]
        bx, by = xs[i], ys[i]
        cx, cy = xs[i + 1], ys[i + 1]
        ab = math.hypot(bx - ax, by - ay)
        bc = math.hypot(cx - bx, cy - by)
        ac = math.hypot(cx - ax, cy - ay)
        area2 = _triangle_area_doubled(ax, ay, bx, by, cx, cy)
        if area2 <= 1e-6 or ab <= 1e-6 or bc <= 1e-6 or ac <= 1e-6:
            radii.append(None)
            continue
        # Circumradius formula: R = (ab * bc * ac) / (4 * Area)
        radius = (ab * bc * ac) / (2.0 * area2)  # since area2 = 2*Area
        radii.append(float(radius))
    return radii


def build_profile_from_points(points: List[Point], elevations: List[Optional[float]]) -> List[Tuple[float, float, float]]:
    """Build (ds, sin(theta), cos(theta)) tuples from XY points and per-point elevations.

    - Points and elevations must be aligned in length.
    - Elevation missing values are linearly interpolated; if impossible, zeros.
    - Assumes metric CRS for XY.
    """
    if len(points) != len(elevations):
        raise ValueError("points and elevations must have the same length")
    n = len(points)
    if n < 2:
        return []
    # Interpolate NaNs in elevations
    z = np.array([np.nan if (e is None or not np.isfinite(e)) else float(e) for e in elevations], dtype=float)
    if np.isnan(z).all():
        z[:] = 0.0
    else:
        # forward fill/backward fill linear
        idx = np.arange(n)
        valid = ~np.isnan(z)
        if not valid[0]:
            first = np.flatnonzero(valid)
            if len(first) > 0:
                z[0] = z[first[0]]
            else:
                z[0] = 0.0
        if not valid[-1]:
            last = np.flatnonzero(valid)
            if len(last) > 0:
                z[-1] = z[last[-1]]
            else:
                z[-1] = 0.0
        # Linear interpolation where possible
        valid = ~np.isnan(z)
        z = np.interp(idx, idx[valid], z[valid])

    xs = np.array([p.x for p in points], dtype=float)
    ys = np.array([p.y for p in points], dtype=float)
    profile: List[Tuple[float, float, float]] = []
    for i in range(n - 1):
        dx = xs[i + 1] - xs[i]
        dy = ys[i + 1] - ys[i]
        ds = float(math.hypot(dx, dy))
        if ds <= 1e-9:
            profile.append((0.0, 0.0, 1.0))
            continue
        dz = float(z[i + 1] - z[i])
        grade = dz / ds
        denom = math.sqrt(1.0 + grade * grade)
        s_sin = grade / denom
        s_cos = 1.0 / denom
        profile.append((ds, s_sin, s_cos))
    return profile


def sample_dem_points(dem_path: str, points: List[Point], src_crs) -> List[Optional[float]]:
    """Sample elevations at given points from a DEM raster, handling CRS transform.

    - points: coordinates in src_crs (same as graph/edges).
    - Returns list of elevation values (can contain None where sampling fails).
    """
    if len(points) == 0:
        return []
    with rasterio.open(dem_path) as ds:
        dem_crs = ds.crs
        transformer = None
        if src_crs is not None and dem_crs is not None and str(src_crs) != str(dem_crs):
            transformer = Transformer.from_crs(src_crs, dem_crs, always_xy=True)
        coords = []
        if transformer is None:
            coords = [(float(p.x), float(p.y)) for p in points]
        else:
            xs = np.array([p.x for p in points], dtype=float)
            ys = np.array([p.y for p in points], dtype=float)
            tx, ty = transformer.transform(xs, ys)
            coords = list(zip(map(float, tx), map(float, ty)))
        values = list(ds.sample(coords))
        out: List[Optional[float]] = []
        for arr in values:
            if arr is None:
                out.append(None)
            else:
                v = float(arr[0]) if len(arr) > 0 else float("nan")
                if np.isnan(v):
                    out.append(None)
                else:
                    out.append(v)
        return out


def cut_linestring_at_length(line: LineString, length: float) -> LineString:
    """Return a portion of the line from 0 to length (clamped).

    Uses shapely.ops.substring if available.
    """
    length = max(0.0, float(length))
    total = float(line.length)
    end = min(length, total)
    if end <= 0.0:
        # return a degenerate line at the start
        start = Point(line.coords[0])
        return LineString([start, start])
    if end >= total:
        return line
    try:
        return shapely_substring(line, 0.0, end, normalized=False)
    except Exception:
        # Fallback: manual interpolation
        pts = [Point(c) for c in line.coords]
        acc = 0.0
        seg_pts = [pts[0]]
        for i in range(len(pts) - 1):
            a = pts[i]
            b = pts[i + 1]
            seg_len = a.distance(b)
            if acc + seg_len < end - 1e-9:
                seg_pts.append(b)
                acc += seg_len
            else:
                # interpolate split
                remain = end - acc
                if seg_len <= 1e-12:
                    seg_pts.append(a)
                else:
                    t = remain / seg_len
                    x = a.x + t * (b.x - a.x)
                    y = a.y + t * (b.y - a.y)
                    seg_pts.append(Point(x, y))
                break
        return LineString(seg_pts)


def build_profile_and_radii(line: LineString, graph_crs, dem_path: str, step_m: float) -> Tuple[List[Tuple[float, float, float]], List[Optional[float]]]:
    """Convenience wrapper to densify a line, sample DEM, and compute profile + radii."""
    pts = densify_linestring(line, step_m)
    elev = sample_dem_points(dem_path, pts, src_crs=graph_crs)
    profile = build_profile_from_points(pts, elev)
    radii = compute_segment_radii(pts)
    return profile, radii




