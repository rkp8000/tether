from __future__ import print_function, division
import unittest

import edr_handling

TEST_EDR_FILE_PATH = '/Users/rkp/Dropbox/arena_data/experiments/stripes_velocity_white_noise_no_odor/150612_113659_stripes_insect04_tr1_ypos_4.EDR'


class TruismsTestCase(unittest.TestCase):

    def test_true_is_true(self):
        self.assertTrue(True)


class EdrFileTestCase(unittest.TestCase):

    def setUp(self):
        data, _, _, header = edr_handling.load_edr(TEST_EDR_FILE_PATH, dt=0)

        self.data = data
        self.header = header

        downsampled_data, _, _, downsampled_header = edr_handling.load_edr(TEST_EDR_FILE_PATH, dt=0.01)
        self.downsampled_data = downsampled_data
        self.downsampled_header = downsampled_header

    def test_correct_number_of_points_marked_in_header(self):

        self.assertEqual(len(self.data), self.header['n_timepoints'])
        self.assertAlmostEqual(self.data[1, 0] - self.data[0, 0], .0002)

    def test_correct_downsampling(self):

        self.assertAlmostEqual(self.downsampled_data[1, 0] - self.downsampled_data[0, 0], .01, delta=.00001)
        self.assertEqual(self.header['n_timepoints'], self.downsampled_header['n_timepoints'])


if __name__ == '__main__':
    unittest.main()