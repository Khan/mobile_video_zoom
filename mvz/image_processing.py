"""Module for taking video frame images and extracting the "center of change".

The "center of change" is defined as the average position of pixels in the
video, weighted by the squared value of the (approximate) time derivative of
the video.

In order to produce the individual frames used, as input, I ran the following
ffmpeg command:
`ffmpeg -i ~/Desktop/AqMT_zB9rP8.mp4 -vsync 1 -r 15 -s 1280x720 -f image2 './test_images/AqMT_zB9rP8_%05d.png'`
"""
import csv
from typing import Iterable, Tuple

import funcy as fn
from PIL import Image, ImageMath

from . import const

n_frames = 1938


def get_frame(frame_index: int) -> Image:
    """Get a PIL.image for the specified 0-indexed frame number."""
    return Image.open(const.fn_base % (frame_index + 1))


def get_frames(frame_count: int, min_frame: int = 0) -> Iterable[Image]:
    """Get frame_count frames starting at min_frame as PIL.images."""
    return (get_frame(i) for i in range(min_frame, min_frame + frame_count))


def image_squared_difference(
        im_tuple: Tuple[Image, Image]) -> Tuple[float, ...]:
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


def weighted_average_pos(im_bands: Tuple[Image, ...]) -> Tuple[float, float]:
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


def main() -> None:
    """Read in the frames of the video, find the center of change.

    Writes out x,y positions to a csv, one row per frame.
    """
    positions = fn.imap(
        weighted_average_pos,
        fn.imap(image_squared_difference,
                fn.pairwise(get_frames(n_frames))))
    with open(const.path_data_fn, 'w') as f:
        csv.writer(f).writerows(positions)
