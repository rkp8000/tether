from __future__ import print_function, division

import os
import numpy as np
import matplotlib.pyplot as plt

import edr_handling

ARENA_DATA_DIRECTORY = os.getenv('ARENA_DATA_DIRECTORY')


class SegmentSelector(object):
    """An extension of a figure in which one can graphically select segments."""

    def __init__(self, fig, axs, t_min=-np.inf, t_max=np.inf, segments=None):
        self.fig = fig
        self.axs = axs
        self.xs = [0]
        self.cid = fig.canvas.mpl_connect('button_press_event', self)

        self.t_min = t_min
        self.t_max = t_max

        # indicator determining whether next click will be start or end of segment
        self.start = True

        self.start_x = None
        self.start_lines = None
        self.segment_color = 'r'

        self.segments = []

        if segments is not None:
            self.make_segments(segments)

    def __call__(self, event):

        if event.button == 3:

            # get clicked location and force it into bounds
            t = event.xdata
            if t > self.t_max:
                t = self.t_max
            if t < self.t_min:
                t = self.t_min

            # if clicked location is within a segment, remove that segment
            for s_ctr, segment in enumerate(self.segments):
                if segment[0] <= t <= segment[1]:
                    # remove start lines (segment[2]), end lines (segment[3]), spans (segment[4])
                    [[obj.remove() for obj in segment[x]] for x in range(2, 5)]
                    self.segments.pop(s_ctr)
                    plt.draw()
                    return

            if self.start:
                # draw a line at the clicked location
                self.start_t = t
                self.start_lines = []
                for ax in self.axs:
                    self.start_lines += [ax.axvline(t, color='k', lw=1)]
            else:
                # fill in a rectangle between the line at the start location and the line at the
                # clicked location
                end_lines = []
                spans = []
                for ax in self.axs:
                    end_lines += [ax.axvline(t, color='k', lw=1)]
                    spans += [ax.axvspan(self.start_t, t, alpha=0.3, color=self.segment_color)]

                # store segment including all start and end lines and spans
                segment = [self.start_t, t]
                if self.start_t > t:
                    segment = segment[::-1]
                    self.start_lines, end_lines = end_lines, self.start_lines

                segment += [self.start_lines, end_lines, spans]

                # add segment to big list and sort them
                self.segments += [segment]
                self.segments = sorted(self.segments, key=lambda seg: seg[0])

            self.start = not self.start

        plt.draw()

    def make_segments(self, segments):
        """Create and plot segments from a list of segments."""
        for segment in segments:
            t_start = segment[0]
            t_end = segment[1]

            lines_start = []
            lines_end = []
            spans = []
            for ax in self.axs:
                lines_start += [ax.axvline(t_start, color='k', lw=1)]
                lines_end += [ax.axvline(t_end, color='k', lw=1)]
                spans += [ax.axvspan(t_start, t_end, alpha=0.3, color=self.segment_color)]
            self.segments += [[t_start, t_end, lines_start, lines_end, spans]]
        plt.draw()

    @property
    def segments_simple(self):
        return [(s[0], s[1]) for s in self.segments]


def plot_trial_basic(trial, fig=None, dt=0, cols=None, **kwargs):
    """Plot the edr file corresponding to a trial."""
    experiment_directory_path = os.path.join(ARENA_DATA_DIRECTORY, trial.experiment.directory_path)
    file_path = os.path.join(experiment_directory_path, trial.file_name)

    data, _, cols, _ = edr_handling.load_edr(file_path, cols=cols, dt=dt)

    if not fig:
        fig = plt.figure(tight_layout=True)

    # the first column of data is the time vector
    n_axs = data.shape[1] - 1
    axs = []
    for a_ctr in range(n_axs):
        ax = fig.add_subplot(n_axs, 1, a_ctr + 1)
        axs += [ax]
        ax.plot(data[:, 0], data[:, a_ctr + 1], **kwargs)
        ax.set_ylabel(cols[a_ctr + 1])

    axs[-1].set_xlabel('time (s)')

    return fig, np.array(axs), data