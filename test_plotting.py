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

    def test_idx_from_time(self):
        fig, axs = plt.subplots(3, 1, sharex=True)

        t = np.linspace(0, 100, 1001)
        segment_selector = plotting.SegmentSelector(fig, axs, time_vector=t)

        self.assertEqual(segment_selector.idx_from_time(.3), 3)
        self.assertEqual(segment_selector.idx_from_time(.29), 3)
        self.assertEqual(segment_selector.idx_from_time(.24), 2)
        self.assertEqual(segment_selector.idx_from_time(50.1), 501)
        self.assertEqual(segment_selector.idx_from_time(50.14), 501)
        self.assertEqual(segment_selector.idx_from_time(-1), 0)
        self.assertEqual(segment_selector.idx_from_time(10000), 1000)


if __name__ == '__main__':
    unittest.main()