"""Bandpass filter the positions, then snap to as few shots as possible."""
from typing import List, Tuple

import funcy as fn
import numpy as np
import pandas as pd
import scipy.signal as sig

from mvz import const
from mvz.methods import shared

freq_cutoff = 0.1
padding = 50


def bandpass_filter_data(data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    b, a = sig.butter(6, freq_cutoff)
    x_filt = sig.lfilter(b, a, data['x'])
    y_filt = sig.lfilter(b, a, data['y'])
    return (x_filt, y_filt)


def choose_window(seq: np.ndarray, window_size: int) -> Tuple[float, int]:
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

    x_frames = make_spec(x_filt[100:],
                         const.box_width,
                         const.max_width)
    y_frames = make_spec(y_filt[100:],
                         const.box_height,
                         const.max_height)

    return x_frames, y_frames


def make_boxes_from_frame_spec(min_frame: int, max_frame: int,
                               xspec: FrameSpec, yspec: FrameSpec) -> (
                                   List[Tuple[int, int, int, int]]):
    key_frames_x = [0] + list(fn.sums([frame for _, frame in xspec]))
    key_frames_y = [0] + list(fn.sums([frame for _, frame in yspec]))

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


def main():
    data = shared.read_path_data(const.path_data_fn)
    x_filt, y_filt = bandpass_filter_data(data)
    x_frames, y_frames = make_frame_specs(x_filt, y_filt)
    boxes = make_boxes_from_frame_spec(
        const.min_frame - 100, const.max_frame - 100,
        x_frames, y_frames)

    shared.crop_to_bounding_boxes(boxes)
