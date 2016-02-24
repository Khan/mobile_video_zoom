#!/usr/bin/env python3.5

import csv
import fix_paths
import os.path

import argparse

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
        '--method', type=str, default='bandpass_and_snapping')
    args = parser.parse_args()
    if not os.path.exists(mvz.const.output_dir):
        os.makedirs(mvz.const.output_dir)
    mvz.downloader.download(args.youtube_id, bust_cache=args.bust_cache)
    mvz.image_processing.main(args.youtube_id, bust_cache=args.bust_cache)
    mvz_methods = __import__('mvz.methods.%s' % args.method).methods
    boxes = getattr(mvz_methods, args.method).main(args.youtube_id)
    mvz.generate_video.main(args.youtube_id, args.method, "auto")

    box_output_fn = os.path.join(
        mvz.const.output_dir, "%s_%s_auto_boxes.csv" % (
            args.youtube_id, args.method))
    with open(box_output_fn, 'w') as f:
        csv.writer(f).writerows(boxes)


if __name__ == '__main__':
    main()
