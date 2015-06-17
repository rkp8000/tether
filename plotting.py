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
            self.show_segments()

        # indicator determining whether next click will be start or end of segment
        self.start = True

        self.start_x = None

        self.ignored_segment_color = 'r'

    def __call__(self, event):
        print('click', event)
        if event.button == 3:
            x = event.xdata
            if self.start:
                # draw a line at the clicked location
                self.start_x = x
                for ax in self.axs:
                    ax.axvline(x, color='k', lw=1)
            else:
                # fill in a rectangle between the line at the start location and the line at the
                # clicked location
                for ax in self.axs:
                    ax.axvline(x, color='k', lw=1)
                    ax.axvspan(self.start_x, x, alpha=0.3, color=self.ignored_segment_color)
                self.segments += [(self.start_x, x)]
            self.start = not self.start
        plt.draw()

    def show_segments(self):
        print('TO DO: make this function show the segments on the axes')


def plot_trial_basic(trial, columns=None):
    """Plot the edr file corresponding to a trial."""
    experiment_directory_path = os.path.join(ARENA_DATA_DIRECTORY, trial.experiment.directory_path)
    file_path = os.path.join(experiment_directory_path, trial.file_name)

    data = edr_handling.load_edr(file_path)[0]