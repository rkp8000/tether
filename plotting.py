from __future__ import print_function, division

import os
import numpy as np
import matplotlib.pyplot as plt

import edr_handling

ARENA_DATA_DIRECTORY = os.getenv('ARENA_DATA_DIRECTORY')


class SegmentSelector(object):
    def __init__(self, fig, axs, segments=None):
        self.fig = fig
        self.axs = axs
        self.xs = [0]
        self.cid = fig.canvas.mpl_connect('button_press_event', self)

        if segments is None:
            self.segments = []
        else:
            self.segments = segments

        # indicator determining whether next click will be start or end of segment
        self.start = True

    def __call__(self, event):
        print('click', event)
        x = event.xdata
        if event.button == 3:
            for ax in self.axs:
                ax.vlines(x, -3, 3, color='k', lw=3)
        plt.draw()


def plot_trial_basic(trial, columns=None):
    """Plot the edr file corresponding to a trial."""
    experiment_directory_path = os.path.join(ARENA_DATA_DIRECTORY, trial.experiment.directory_path)
    file_path = os.path.join(experiment_directory_path, trial.file_name)

    data = edr_handling.load_edr(file_path)[0]