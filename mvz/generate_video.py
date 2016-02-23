"""Generate a new video from a sequence of frame images.

For now, the frame images
"""
import matplotlib

from mvz import const

matplotlib.use("Agg")
import matplotlib.pyplot as pl
import matplotlib.animation


fps = 15
dpi = 72

video_output_template = (
    "/Users/colin/Desktop/image_output/movie_output/%s_%s.mp4")


def main(method_name: str, method_param: str) -> None:
    FFMpegWriter = matplotlib.animation.writers['ffmpeg']
    metadata = {'title': 'Simple smoothing'}
    writer = FFMpegWriter(fps=fps, metadata=metadata)

    fig = pl.figure(
        figsize=(const.box_width/float(dpi), const.box_height/float(dpi)))
    ax = pl.Axes(pl.gcf(), [0, 0, 1, 1], yticks=[], xticks=[], frame_on=False)
    pl.gcf().delaxes(fig.gca())
    pl.gcf().add_axes(ax)

    imobj = None

    video_fn = video_output_template % (method_name, method_param)

    with writer.saving(fig, video_fn, dpi):
        for i in range(const.min_frame, const.max_frame):
            frame_fn = const.output_format_string % (i+1)
            im = pl.imread(frame_fn)
            if imobj is None:
                imobj = pl.imshow(im)
            else:
                imobj.set_data(im)
            pl.pause(0.001)
            writer.grab_frame()
