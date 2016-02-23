# TODO(colin): don't hardcode these
video_id = 'AqMT_zB9rP8'
fn_base = (("/Users/colin/khan/mobile-video-zoom/test_images/%s" % video_id) +
           "_%05d.png")
path_data_fn = "/Users/colin/khan/mobile-video-zoom/path_data.csv"

output_format_string = "/Users/colin/Desktop/image_output/image-%05d_out.png"

# The size of the mobile video player target in px
box_width = 432
box_height = 243

# The size of the video in px (we could probably just infer this?)
max_width = 1280
max_height = 720

# The frames we're currently sampling for testing
min_frame = 1200
max_frame = 1500
