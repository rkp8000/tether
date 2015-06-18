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
        instructions = ('\n'
                        'Right click on the plot to highlight segments.\n'
                        'Use the normal cursors to move/zoom as you do so.\n'
                        'To remove a segment, right click somewhere in the middle of it.\n'
                        'When you are satisfied, you can close the window.')
        print(instructions)

        fig, axs = plt.subplots(2, 1, sharex=True)

        t = np.linspace(0, 100, 1001)
        x0 = np.random.normal(0, 1, t.shape)
        x1 = np.random.normal(0, 1, t.shape)

        axs[0].plot(t, x0)
        axs[1].plot(t, x1)

        plotting.SegmentSelector(fig, axs, t[0], t[-1])

        plt.show()

    def test_load_with_set_of_segments(self):
        instructions = ('\n'
                       'This plot has been opened with some segments pre-loaded.\n'
                       'Feel free to modify them in the same way as before.\n'
                       'When you close this plot, the segments will be saved and they will be loaded automatically with the plot that follows.')
        print(instructions)

        fig, axs = plt.subplots(2, 1, sharex=True)

        t = np.linspace(0, 100, 1001)
        x0 = np.random.normal(0, 1, t.shape)
        x1 = np.random.normal(0, 1, t.shape)

        segments = [(0, 10), (20.4, 29.1), (90, 96)]
        axs[0].plot(t, x0)
        axs[1].plot(t, x1)

        segment_selector = plotting.SegmentSelector(fig, axs, t[0], t[-1], segments)

        plt.show()

        # save the segments from this SegmentSelector
        segments = segment_selector.segments_simple

        # load a new SegmentSelector using the segments from the one that was just closed
        fig, axs = plt.subplots(2, 1, sharex=True)

        t = np.linspace(0, 100, 1001)
        x0 = np.random.normal(0, 1, t.shape)
        x1 = np.random.normal(0, 1, t.shape)

        axs[0].plot(t, x0)
        axs[1].plot(t, x1)

        segment_selector2 = plotting.SegmentSelector(fig, axs, t[0], t[-1], segments)

        plt.show()

if __name__ == '__main__':
    unittest.main()