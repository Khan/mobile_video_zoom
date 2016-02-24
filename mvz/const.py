import os.path
from typing import Tuple

import funcy as fn

# TODO(colin): don't hardcode these
video_id = 'AqMT_zB9rP8'

url_for_youtube_id = (
    'http://fastly.kastatic.org/KA-youtube-converted'
    '/%(yt_id)s.mp4/%(yt_id)s.mp4')

cache_dir = "./cache"
output_dir = "./output"

# The size of the mobile video player target in px
# Original testing was done at 432 x 243
box_width = 400
box_height = box_width

# The size of the video in px (we could probably just infer this?)
max_width = 1280
max_height = 720

# The frames we're currently sampling for testing
min_frame = 0
max_frame = 1938

BoundingBox = Tuple[int, int, int, int]


def video_fn(youtube_id: str) -> str:
    return os.path.join(cache_dir, '%s.mp4' % youtube_id)


def frame_fn_template(youtube_id: str) -> str:
    return os.path.join(cache_dir, '%s_%%06d.png' % youtube_id)


def path_data_fn(youtube_id: str) -> str:
    return os.path.join(cache_dir, '%s_path_data.csv' % youtube_id)


def output_frame_template(youtube_id: str) -> str:
    return os.path.join(output_dir, '%s_%%06d.png' % youtube_id)


def output_video_fn(youtube_id: str, method: str, param: str) -> str:
    return os.path.join(output_dir, '%s_%s_%s.mp4' % (
        youtube_id, method, param))
