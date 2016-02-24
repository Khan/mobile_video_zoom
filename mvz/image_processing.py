"""Module for taking video frame images and extracting the "center of change".

The "center of change" is defined as the average position of pixels in the
video, weighted by the squared value of the (approximate) time derivative of
the video.
"""
import csv
import os.path
from typing import Iterable, List, Tuple

import funcy as fn
from PIL import Image
from PIL import ImageMath

from . import const


def n_frames(youtube_id: str) -> int:
    # TODO(colin): somehow unite this with the filename in the const module
    extractor = r'%s_(\d+).png' % youtube_id
    return fn.rcompose(
        os.listdir,
        fn.partial(fn.filter, extractor),
        fn.partial(fn.map, extractor),
        fn.partial(fn.map, int),
        max)(const.cache_dir)


def get_frame(youtube_id: str, frame_index: int) -> Image.Image:
    """Get a PIL.image for the specified 0-indexed frame number."""
    return Image.open(const.frame_fn_template(youtube_id) % (frame_index + 1))


def get_frames(youtube_id: str, frame_count: int, min_frame: int = 0) -> (
        Iterable[Image.Image]):
    """Get frame_count frames starting at min_frame as PIL.images."""
    return (get_frame(youtube_id, i)
            for i in range(min_frame, min_frame + frame_count))


def image_squared_difference(
        im_tuple: Tuple[Image.Image, Image.Image]) -> Tuple[float, ...]:
    """Find the squared difference between two images.

    Args:
        im_tuple: a two-item tuple of PIL images.

    Return:
        a tuple containing an Image for each band in the input images.
    """
    im0, im1 = im_tuple
    parts1 = im1.split()
    parts0 = im0.split()
    bands = tuple(
        ImageMath.eval("(b - a)**2", b=p1, a=p0)
        for p1, p0 in zip(parts1, parts0)
    )
    return bands


def weighted_average_pos(im_bands: Tuple[Image.Image, ...]) -> (
        Tuple[float, float]):
    """Find the average position in the image weighted by the image values.

    All bands are weighted equally.

    Note that this is the only particularly slow step in the image processing;
    this might be worth trying to rewrite with better use of PIL or numpy ops
    or moving to C.
    """
    pixel_sum = 0.0
    weighted_average_x = 0.0
    weighted_average_y = 0.0

    for im in im_bands:
        px = im.load()
        for x in range(im.width):
            for y in range(im.height):
                pixel_sum += px[x, y]
                weighted_average_x += x * px[x, y]
                weighted_average_y += y * px[x, y]
    if pixel_sum == 0:
        return (float('NaN'), float('NaN'))
    return (weighted_average_x / pixel_sum, weighted_average_y / pixel_sum)


def main(youtube_id: str, bust_cache: bool = False) -> (
        List[Tuple[float, float]]):
    """Read in the frames of the video, find the center of change.

    Writes out x,y positions to a csv, one row per frame.
    """
    path_data_fn = const.path_data_fn(youtube_id)

    if not os.path.exists(path_data_fn) or bust_cache:
        positions = fn.rcompose(
            n_frames,
            fn.partial(get_frames, youtube_id),
            fn.pairwise,
            fn.partial(fn.map, image_squared_difference),
            fn.partial(fn.map, weighted_average_pos),
            list)(youtube_id)

        with open(const.path_data_fn(youtube_id), 'w') as f:
            csv.writer(f).writerows(positions)
        return positions
    else:
        with open(const.path_data_fn(youtube_id), 'r') as f:
            return [(float(line[0]), float(line[1])) for line in csv.reader(f)]
