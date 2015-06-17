from __future__ import division, print_function

import unittest

import numpy as np
import matplotlib.pyplot as plt

import plotting


class TruismsTestCase(unittest.TestCase):

    def test_truisms(self):
        self.assertTrue(True)


class SegmentSelectorTestCase(unittest.TestCase):

    def test_correct_number_of_segments_stored(self):
        fig, axs = plt.subplots(2, 1, sharex=True)

        t = np.linspace(0, 100, 1000)
        x0 = np.random.normal(0, 1, t.shape)
        x1 = np.random.normal(0, 1, t.shape)

        axs[0].plot(t, x0)
        axs[1].plot(t, x1)

        segment_selector = plotting.SegmentSelector(fig, axs, time_vector=t)

        plt.show()

        print(segment_selector.segments)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()