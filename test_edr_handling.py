from __future__ import print_function, division
import unittest

from db_api import models
from db_api.connect import session

import edr_handling

TEST_EDR_FILE_PATH = '/Users/rkp/Dropbox/arena_data/experiments/stripes_velocity_white_noise_no_odor/150612_113659_stripes_insect04_tr1_ypos_4.EDR'
TEST_TRIAL_ID = 2


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


class LoadFromTrialTestCase(unittest.TestCase):

    def test_segments_correctly_loaded(self):
        trial = session.query(models.Trial).get(1)

        trial.ignored_segments = []
        trial.ignored_segments += [models.IgnoredSegment(start_time=10, end_time=20)]
        trial.ignored_segments += [models.IgnoredSegment(start_time=100, end_time=200)]

        # make sure segments load correctly with one dt
        data, _, _, _ = edr_handling.load_from_trial(trial, dt=.01)

        self.assertEqual(len(data), 3)
        self.assertAlmostEqual(data[0][0, 0], 0, delta=.00001)
        self.assertAlmostEqual(data[0][-1, 0], 9.99, delta=.03)
        self.assertAlmostEqual(data[1][0, 0], 20, delta=.03)
        self.assertAlmostEqual(data[1][-1, 0], 99.99, delta=.03)

        # make sure segments load correctly with another dt
        data, _, _, _ = edr_handling.load_from_trial(trial, dt=.005)

        self.assertEqual(len(data), 3)
        self.assertAlmostEqual(data[0][0, 0], 0, delta=.00001)
        self.assertAlmostEqual(data[0][-1, 0], 9.99, delta=.03)
        self.assertAlmostEqual(data[1][0, 0], 20, delta=.03)
        self.assertAlmostEqual(data[1][-1, 0], 99.99, delta=.03)

        session.rollback()

    def test_segments_correctly_loaded_with_beginning_ignored_segments(self):
        trial = session.query(models.Trial).get(1)

        trial.ignored_segments = []
        trial.ignored_segments += [models.IgnoredSegment(start_time=0, end_time=20)]
        trial.ignored_segments += [models.IgnoredSegment(start_time=100, end_time=200)]

        data, _, _, _ = edr_handling.load_from_trial(trial, dt=.01)

        self.assertEqual(len(data), 2)

        session.rollback()

        trial = session.query(models.Trial).get(1)

        trial.ignored_segments = []
        trial.ignored_segments += [models.IgnoredSegment(start_time=0.05, end_time=20)]
        trial.ignored_segments += [models.IgnoredSegment(start_time=100, end_time=200)]

        data, _, _, _ = edr_handling.load_from_trial(trial, dt=.01)

        self.assertEqual(len(data), 2)

        session.rollback()

        trial = session.query(models.Trial).get(1)

        trial.ignored_segments = []
        trial.ignored_segments += [models.IgnoredSegment(start_time=0.11, end_time=20)]
        trial.ignored_segments += [models.IgnoredSegment(start_time=100, end_time=200)]

        data, _, _, _ = edr_handling.load_from_trial(trial, dt=.01)

        self.assertEqual(len(data), 3)

        session.rollback()

if __name__ == '__main__':
    unittest.main()