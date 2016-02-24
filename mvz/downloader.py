from io import BytesIO
import os.path
import subprocess

import requests as req

import mvz.const as const


def download(youtube_id: str, bust_cache: bool = False) -> str:
    url = const.url_for_youtube_id % {'yt_id': youtube_id}
    video = BytesIO(req.get(url).content)
    video_fn = const.video_fn(youtube_id)

    if not os.path.exists(const.cache_dir):
        os.makedirs(const.cache_dir)

    if not os.path.exists(video_fn) or bust_cache:
        with open(video_fn, 'wb') as f:
            f.write(video.read())

        split_into_frames(youtube_id)

    return video_fn


def split_into_frames(youtube_id: str) -> None:
    command = (
        "ffmpeg -i %(video_fn)s -vsync 1 -r 15 -s 1280x720"
        " -f image2 '%(output_fn_template)s'") % {
            'video_fn': const.video_fn(youtube_id),
            'output_fn_template': const.frame_fn_template(youtube_id)}
    subprocess.call(command, shell=True)
