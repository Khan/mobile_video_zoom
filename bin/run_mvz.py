#!/usr/bin/env python3.5

import csv
import json
import os.path

import argparse

import fix_paths
import mvz.const
import mvz.downloader
import mvz.generate_video
import mvz.image_processing


def main():
    parser = argparse.ArgumentParser(
        description='process a video into a candidate mobile video sequence')
    parser.add_argument('youtube_id', type=str,
                        help='the youtube id of the video to process')
    parser.add_argument(
        '--bust-cache', action='store_true',
        help='refetch the video from youtube and reprocess everything')
    parser.add_argument(
        '--all-frames', action='store_true',
        help='write output for every frame, not only for the keyframe positions')
    parser.add_argument(
        '--json', action='store_true',
        help='write output as json arrays instead of csv')
    parser.add_argument(
        '--method', type=str, default='bandpass_and_snapping')
    args = parser.parse_args()
    if not os.path.exists(mvz.const.output_dir):
        os.makedirs(mvz.const.output_dir)
    mvz.downloader.download(args.youtube_id, bust_cache=args.bust_cache)
    (_, video_width, video_height) = mvz.image_processing.main(args.youtube_id, bust_cache=args.bust_cache)
    mvz_methods = __import__('mvz.methods.%s' % args.method).methods
    boxes = getattr(mvz_methods, args.method).main(
        args.youtube_id,
        frame_count=mvz.image_processing.n_frames(args.youtube_id),
        keyframes_only=not args.all_frames,
        video_width=video_width,
        video_height=video_height
    )
    if args.all_frames:
        mvz.generate_video.main(args.youtube_id, args.method, "auto")

    extension = "json" if args.json else "csv"

    box_output_fn = os.path.join(
        mvz.const.output_dir, "%s_%s_auto_boxes.%s" % (
            args.youtube_id, args.method, extension))
    with open(box_output_fn, 'w') as f:
        if args.json:
            f.write(json.dumps(boxes))
        else:
            csv.writer(f).writerows(boxes)


if __name__ == '__main__':
    main()
