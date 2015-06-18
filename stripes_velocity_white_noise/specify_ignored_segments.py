"""
Go through a set of trials corresponding to this experiment and graphically specify what
temporal segments to ignore.
"""
from __future__ import print_function, division

import datetime
import numpy as np
import matplotlib.pyplot as plt

from db_api.connect import session
from db_api import models

import edr_handling
from plotting import SegmentSelector, plot_trial_basic

EXPERIMENT_ID = 'stripes_velocity_white_noise_no_odor'
EARLIEST_DATETIME = datetime.datetime.strptime('2015-06-15', '%Y-%m-%d')


def main():
    # print instructions
    print('Right click on trial to mark starts and ends of segments.')
    print('Close window to move on to next trial.')

    trials = session.query(models.Trial). \
        filter(models.Trial.experiment_id == EXPERIMENT_ID). \
        filter(models.Trial.recording_start >= EARLIEST_DATETIME)

    for trial in trials[:3]:
        fig = plt.figure(facecolor='white')
        fig, axs, edr_data = plot_trial_basic(trial, fig, dt=.01)

        if trial.ignored_segments:
            ignored_segments = [(i_s.start_time_idx, i_s.end_time_idx) for i_s in trial.ignored_segments]
        else:
            ignored_segments = None
        segment_selector = SegmentSelector(fig, axs, time_vector=edr_data[:, 0], segments_idx=ignored_segments)

        plt.show(block=True)

        # remove all ignored segments that were previously bound to this trial
        [session.delete(i_s) for i_s in trial.ignored_segments]
        trial.ignored_segments = []

        for segment_idx in segment_selector.segments_idx:
            ignored_segment = models.IgnoredSegment()
            # convert time to time idx
            ignored_segment.start_time_idx = segment_idx[0]
            ignored_segment.end_time_idx = segment_idx[1]

            trial.ignored_segments += [ignored_segment]

    save = raw_input('Save [y or n]?')

    if save.lower() == 'y':
        # add all updated trials to database
        for trial in trials:
            session.add(trial)
        session.commit()
    else:
        print('Data not saved.')
        session.rollback()

if __name__ == '__main__':
    main()