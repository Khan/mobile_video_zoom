from typing import Tuple

import pandas as pd

from mvz import const
from mvz.methods import shared

smoothing_span = 1


def smooth_with_ewma(data: pd.DataFrame, window: int) -> pd.DataFrame:
    return pd.ewma(data, span=window)


def box_for_position(pos: Tuple[int, int])-> Tuple[int, int, int, int]:
    """Given a position, get a bounding box centered at that position.

    Bounding box is [left, top, right, bottom].
    """
    origin = [max(pos[0] - const.box_width/2, 0),
              max(pos[1] - const.box_height/2, 0)]
    if origin[0] + const.box_width > const.max_width:
        origin[0] = const.max_width - const.box_width
    if origin[1] + const.box_height > const.max_height:
        origin[1] = const.max_height - const.box_height

    return shared.tuple4(tuple(
        int(round(coord))
        for coord in (origin[0], origin[1],
                      origin[0] + const.box_width,
                      origin[1] + const.box_height)))


def crop_all_to_bounding_box(frame_count: int) -> None:
    smoothed_np = smooth_with_ewma(
        shared.read_path_data(const.path_data_fn),
        smoothing_span).values

    boxes = (box_for_position(smoothed_np[i])
             for i in range(0, frame_count))

    shared.crop_to_bounding_boxes(boxes)

main = crop_all_to_bounding_box
