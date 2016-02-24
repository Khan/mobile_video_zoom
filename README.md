## Installation

Requires python >= 3.5.

Install ffmpeg:
`brew install ffmpeg`

Install python dependencies:
`pip install -r requirements.txt`

Optionally, install extra dev tools:
`pip install ipython`
`pip install git+git://github.com/python/mypy.git`

## Running

From the project root directory, run:
`bin/run_mvz.py <youtube_id>`

If this has never been run on the video before, this will take a long time (in
the neighborhood of ~15 min per 1 min of video).  In the future, the slow image
processing steps are cached in the `./cache` directory.  (You can bust the
cache and recompute everything by running `bin/run_mvz.py --bust-cache
<youtube_id>`.)

Output ends up in the `./output` directory.  There will be one png for each
frame (which you can probably ignore), one mp4 file containing the cropped
output video, and a csv containing bounding boxes for each frame.  The csv has
one line per 1/15s frame, with columns left, top, right, bottom coordinates.
(The coordinate system is such that upper left is (0, 0).)
