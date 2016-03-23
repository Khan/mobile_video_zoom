from typing import Iterable, Tuple, Union, List

import pandas as pd
from PIL import Image

from mvz import const

# If the x value dips below this, we remove the point.  This helps deal with
# when Sal goes to change colors in the video and the cursor moves all the way
# to the left.
min_value_x = 100

Frame = Tuple[float, int, int, int, int]
Frames = List[Tuple[float, int, int, int, int]]
FrameSpecOutput = Union[List[const.BoundingBox],
                        List[Tuple[float, int, int, int, int]]]

NormalizedFrame = Tuple[float, float, float, float, float]
NormalizedFrames = List[Tuple[float, float, float, float, float]]

def read_path_data(path_data_fn: str) -> pd.DataFrame:
    """Read the path data output by the image processing step.

    Return a pandas dataframe with NaN values filled with the previous value.
    """
    data = pd.read_csv(path_data_fn, header=None, names=['x', 'y'])
    data['y'][data['x'] < min_value_x] = float('NaN')
    data['x'][data['x'] < min_value_x] = float('NaN')
    return data.fillna(method='pad')


def crop_to_bounding_boxes(youtube_id: str,
                           frame_count: int,
                           boxes: Iterable[const.BoundingBox]):
    for i, box in zip(range(0, frame_count), boxes):
        im = Image.open(const.frame_fn_template(youtube_id) % (i + 1))
        cropped = im.crop(box=box)
        cropped.save(const.output_frame_template(youtube_id) % (i + 1))


def normalize_boxes(boxes: Frames,
                    video_width: int, video_height: int) -> NormalizedFrames:
    def normalize_box(box: Frame) -> NormalizedFrame:
        def normalize_horizontal_dimension(d: int) -> float:
            return d / video_width

        def normalize_vertical_dimension(d: int) -> float:
            return d / video_height

        (frame, x, y, w, h) = box

        return (frame,
                normalize_horizontal_dimension(x), normalize_vertical_dimension(y),
                normalize_horizontal_dimension(w), normalize_vertical_dimension(h))

    return map(normalize_box, boxes)


def tuple4(tuple_n: Tuple[int, ...]) -> Tuple[int, int, int, int]:
    # Sadly, mypy can't infer that all our bounding boxes are a 4-element
    # tuple, or that tuple_n[0:3] is either.
    # TODO(colin): use one of those when type inference is better!
    return (tuple_n[0], tuple_n[1], tuple_n[2], tuple_n[3])
