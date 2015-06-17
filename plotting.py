from __future__ import print_function, division

import os
import numpy as np
import matplotlib.pyplot as plt

import edr_handling

ARENA_DATA_DIRECTORY = os.getenv('ARENA_DATA_DIRECTORY')


class SegmentSelector(object):
    """An extension of a figure in which one can graphically select segments."""

    def __init__(self, fig, axs, segments=None, time_vector=None):
        self.fig = fig
        self.axs = axs
        self.xs = [0]
        self.cid = fig.canvas.mpl_connect('button_press_event', self)

        if segments is None:
            self.segments = []
        else:
            self.segments = segments
            self.show_segments()

        self.time_vector = time_vector
        if self.time_vector is not None:
            self.t_min = self.time_vector[0]
            self.t_max = self.time_vector[-1]
        else:
            self.t_min = -np.inf
            self.t_max = np.inf

        # indicator determining whether next click will be start or end of segment
        self.start = True

        self.start_x = None

        self.segment_color = 'r'

    def __call__(self, event):

        if event.button == 3:
            # get clicked location and force it into bounds
            t = event.xdata
            if t > self.t_max:
                t = self.t_max
            if t < self.t_min:
                t = self.t_min

            if self.start:
                # draw a line at the clicked location
                self.start_t = t
                for ax in self.axs:
                    ax.axvline(t, color='k', lw=1)
            else:
                # store segment
                segment = (self.start_t, t)
                if self.start_t > t:
                    segment = segment[::-1]
                self.segments += [segment]

                self.segments = sorted(self.segments, key=lambda seg: seg[0])

                # fill in a rectangle between the line at the start location and the line at the
                # clicked location
                for ax in self.axs:
                    ax.axvline(t, color='k', lw=1)
                    ax.axvspan(self.start_t, t, alpha=0.3, color=self.segment_color)

            self.start = not self.start

        plt.draw()

    def show_segments(self):
        print('TO DO: make this function show the segments on the axes')

    def idx_from_time(self, t):
        """
        Use self.time_vector to compute the index of the time in time vector that is
        nearest to t.
        :param t: floating point time
        :return:
        """
        if self.time_vector is None:
            raise TypeError('time_vector is not defined')

        dt = self.time_vector[1] - self.time_vector[0]
        idx = int(round(t / dt))
        if idx < 0:
            idx = 0
        elif idx > len(self.time_vector) - 1:
            idx = len(self.time_vector) - 1

        return idx

    @property
    def segment_idxs(self):
        return [(self.idx_from_time(s[0]), self.idx_from_time(s[1])) for s in self.segments]


def plot_trial_basic(trial, columns=None):
    """Plot the edr file corresponding to a trial."""
    experiment_directory_path = os.path.join(ARENA_DATA_DIRECTORY, trial.experiment.directory_path)
    file_path = os.path.join(experiment_directory_path, trial.file_name)

    data = edr_handling.load_edr(file_path)[0]