import os.path
from typing import Tuple

# TODO(colin): don't hardcode these
video_id = 'AqMT_zB9rP8'
fn_base = os.path.expanduser(
    ("~/khan/mobile-video-zoom/test_images/%s" % video_id) +
    "_%05d.png")
path_data_fn = os.path.expanduser(
    "~/khan/mobile-video-zoom/path_data.csv")

output_format_string = os.path.expanduser(
    "~/Desktop/image_output/image-%05d_out.png")

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
