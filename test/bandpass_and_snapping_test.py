import nose.tools as n

import mvz.methods.bandpass_and_snapping as bas


def distance_to_next_change_test():
    subject = [0, 0, 0, 1]
    n.eq_(bas.distance_to_next_change(subject, 0), 3)
    n.eq_(bas.distance_to_next_change(subject, 1), 2)
    n.eq_(bas.distance_to_next_change(subject, 3), None)
