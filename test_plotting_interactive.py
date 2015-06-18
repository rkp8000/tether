from __future__ import division, print_function

import unittest

import pprint as pp
import numpy as np
import matplotlib.pyplot as plt

import plotting


class TruismsTestCase(unittest.TestCase):

    def test_truisms(self):
        self.assertTrue(True)


class SegmentSelectorTestCase(unittest.TestCase):

    def test_correct_number_of_segments_stored(self):
        fig, axs = plt.subplots(2, 1, sharex=True)

        t = np.linspace(0, 100, 1001)
        x0 = np.random.normal(0, 1, t.shape)
        x1 = np.random.normal(0, 1, t.shape)

        axs[0].plot(t, x0)
        axs[1].plot(t, x1)

        plotting.SegmentSelector(fig, axs, time_vector=t)

        plt.show()

    def test_load_with_set_of_segments(self):
        fig, axs = plt.subplots(2, 1, sharex=True)

        t = np.linspace(0, 100, 1001)
        x0 = np.random.normal(0, 1, t.shape)
        x1 = np.random.normal(0, 1, t.shape)

        segments = [(0, 100), (200, 400), (900, 999)]
        axs[0].plot(t, x0)
        axs[1].plot(t, x1)

        segment_selector = plotting.SegmentSelector(fig, axs, time_vector=t, segments_idx=segments)

        plt.show()

        # save the segments from this SegmentSelector
        segments = segment_selector.segments_idx

        # load a new SegmentSelector using the segments from the one that was just closed
        fig, axs = plt.subplots(2, 1, sharex=True)

        t = np.linspace(0, 100, 1001)
        x0 = np.random.normal(0, 1, t.shape)
        x1 = np.random.normal(0, 1, t.shape)

        axs[0].plot(t, x0)
        axs[1].plot(t, x1)

        segment_selector2 = plotting.SegmentSelector(fig, axs, time_vector=t, segments_idx=segments)

        plt.show()

if __name__ == '__main__':
    unittest.main()