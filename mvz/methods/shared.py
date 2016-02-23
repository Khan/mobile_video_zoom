from typing import Iterable, Tuple

import pandas as pd
from PIL import Image

from mvz import const


def load_path_data():
    pass


def read_path_data(path_data_fn: str) -> pd.DataFrame:
    """Read the path data output by the image processing step.

    Return a pandas dataframe with NaN values filled with the previous value.
    """
    data = pd.read_csv(path_data_fn, header=None, names=['x', 'y'])
    return data.fillna(method='pad')


def crop_to_bounding_boxes(boxes: Iterable[Tuple[int, int, int, int]]):
    for i, box in zip(range(const.min_frame, const.max_frame), boxes):
        im = Image.open(const.fn_base % (i+1))
        cropped = im.crop(box=box)
        cropped.save(const.output_format_string % (i+1))


def tuple4(tuple_n: Tuple[int, ...]) -> Tuple[int, int, int, int]:
    # Sadly, mypy can't infer that all our bounding boxes are a 4-element
    # tuple, or that tuple_n[0:3] is either.
    # TODO(colin): use one of those when type inference is better!
    return (tuple_n[0], tuple_n[1], tuple_n[2], tuple_n[3])
