"""Bandpass filter the positions, then snap to as few shots as possible."""
from typing import Any, List, Optional, Tuple

import funcy as fn
import numpy as np
import pandas as pd
import scipy.signal as sig
import scipy.stats as stats

from mvz import const
from mvz.methods import shared

anticipation_time = 30
freq_cutoff = 0.05
padding = 80
initial_offset = 0


def bandpass_filter_data(data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Lowpass filter the supplied x, y data."""
    b, a = sig.butter(6, freq_cutoff)
    x_filt = sig.lfilter(b, a, data['x'])
    y_filt = sig.lfilter(b, a, data['y'])
    return (x_filt, y_filt)


def choose_window(seq: np.ndarray, window_size: int) -> Tuple[float, int]:
    """Find the maximum length time window until action exits the box.

    Returns a tuple of the minimum value in the box and the number of frames to
    stay in that box.
    """
    prev_min = 0.0
    minval = float('Infinity')
    maxval = 0.0
    index = -1
    while (maxval - minval) < window_size:
        index += 1
        prev_min = minval
        if index == len(seq):
            break
        minval = min(minval, seq[index])
        maxval = max(maxval, seq[index])
    return (prev_min, index)


FrameSpec = List[Tuple[float, int]]


def make_frame_specs(x_filt: np.ndarray, y_filt: np.ndarray) -> (
        Tuple[FrameSpec, FrameSpec]):

    def make_spec(seq: np.ndarray, box_size: int, max_size: int) -> FrameSpec:
        frames = []
        while len(seq) > 0:
            start, idx = choose_window(seq, box_size - padding)
            if start < 0:
                start = 0
            if start > max_size - box_size:
                start = max_size - box_size
            frames.append((start, idx))
            seq = seq[idx:]
        return frames

    x_frames = make_spec(x_filt[initial_offset:],
                         const.box_width,
                         const.max_width)
    y_frames = make_spec(y_filt[initial_offset:],
                         const.box_height,
                         const.max_height)

    return x_frames, y_frames


def make_boxes_from_frame_spec(min_frame: int, max_frame: int,
                               xspec: FrameSpec, yspec: FrameSpec) -> (
                                   List[const.BoundingBox]):
    key_frames_x = [0] + list(fn.sums([frame for _, frame in xspec]))[:-1]
    key_frames_y = [0] + list(fn.sums([frame for _, frame in yspec]))[:-1]

    def key_frame_index(key_frames, frame):
        for ki, k in enumerate(key_frames):
            if k > frame:
                return ki - 1
        return len(key_frames) - 1

    frame_pos_x = map(
        lambda key_idx: int(round(xspec[key_idx][0])),
        map(
            fn.curry(key_frame_index)(key_frames_x),
            range(min_frame, max_frame)))
    frame_pos_y = map(
        lambda key_idx: int(round(yspec[key_idx][0])),
        map(
            fn.curry(key_frame_index)(key_frames_y),
            range(min_frame, max_frame)))

    return [shared.tuple4(tuple(
        int(round(coord))
        for coord in (pos_x - padding/2, pos_y - padding/2, pos_x - padding/2 +
                      const.box_width, pos_y - padding/2 + const.box_height)
        )) for pos_x, pos_y in zip(frame_pos_x, frame_pos_y)]


def distance_to_next_change(boxes: List[Any], idx: int) -> Optional[int]:
    """Given a sequence and an index, find the number of elements to the next
    value that's different from the current one.
    """
    remboxes = boxes[idx:] + [None]
    dist = fn.ilen(fn.takewhile(lambda b: b == boxes[idx], remboxes))
    if remboxes[dist] is None:
        return None
    return dist


def _interpolate1(start_coord: int, finish_coord: int, distance: int) -> int:
    mean = float(anticipation_time) / 2
    scale = anticipation_time / 6
    frac = stats.norm.cdf(anticipation_time - distance, loc=mean, scale=scale)
    return int(round(start_coord + (finish_coord - start_coord) * frac))


def interpolate(start_box: const.BoundingBox, finish_box: const.BoundingBox,
                distance: int) -> const.BoundingBox:
    return shared.tuple4(tuple(
        _interpolate1(start_coord, final_coord, distance)
        for start_coord, final_coord in zip(start_box, finish_box)))


def anticipate_changes(
        boxes: List[const.BoundingBox]) -> List[const.BoundingBox]:
    should_anticipate = [
        idx < len(boxes) - anticipation_time and
        boxes[idx] != boxes[idx + anticipation_time]
        for idx in range(len(boxes))]

    new_boxes = []
    for i, box in enumerate(boxes):
        if should_anticipate[i]:
            dist = distance_to_next_change(boxes, i)
            result = interpolate(
                box, boxes[i + dist], dist)
        else:
            result = box
        new_boxes.append(result)
    return new_boxes

    return boxes


def main():
    data = shared.read_path_data(const.path_data_fn)
    x_filt, y_filt = bandpass_filter_data(data)
    x_frames, y_frames = make_frame_specs(x_filt, y_filt)
    boxes = make_boxes_from_frame_spec(
        const.min_frame - initial_offset, const.max_frame - initial_offset,
        x_frames, y_frames)
    boxes = anticipate_changes(boxes)

    shared.crop_to_bounding_boxes(boxes)
