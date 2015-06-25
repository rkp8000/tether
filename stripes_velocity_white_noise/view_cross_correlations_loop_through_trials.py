"""
Plot the cross-correlations between the following pairs of variables for a specified trial:

velocity vs. left-minus-right
velocity vs. frequency
absolute velocity vs. frequency
"""
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sp_signal

from math_tools import signal

from db_api import models
from db_api.connect import session

import edr_handling

PLOT_TIME_SERIES = False
PLOT_AUTO_CORRELATIONS = True
PLOT_P_VALUES = False

FIG_SIZE_TIME_SERIES = (16, 16)

TRIAL_IDS = xrange(1, 36)
LAG_FORWARD = 5  # in seconds
LAG_BACK = 0.5  # in seconds
DT = .04  # in seconds

# for building the control time-series (to make sure things work!)
CONTROL_FILTER_T = np.linspace(0, LAG_FORWARD, int(LAG_FORWARD/DT), endpoint=False)
CONTROL_FILTER = .1 * np.exp(-CONTROL_FILTER_T / 1.)
CONTROL_SHIFT = 20
CONTROL_FILTER = np.concatenate([np.zeros(20,), CONTROL_FILTER[:-CONTROL_SHIFT]])
CONTROL_NOISE = 0.000001
N_TIMESTEPS_FILTER = len(CONTROL_FILTER)

# for building a random time-series
STIM_RANDOM_NOISE = 100

LW = 2
ALPHA = 0.3


def main():
    for trial_id in TRIAL_IDS:

        print('Trial {}'.format(trial_id))
        trial = session.query(models.Trial).get(trial_id)

        data, _, cols, _ = edr_handling.load_from_trial(trial, dt=DT, unwrap_barpos=True, lmr_zscore=False)

        pos = [data_segment[:, cols.index('Barpos')] for data_segment in data]
        vel = [np.gradient(pos_segment) / DT for pos_segment in pos]
        vel_abs = [np.abs(vel_segment) for vel_segment in vel]
        lmr = [data_segment[:, cols.index('LmR')] for data_segment in data]
        lpr = [data_segment[:, cols.index('Lamp')] + data_segment[:, cols.index('Ramp')]
               for data_segment in data]
        freq = [data_segment[:, cols.index('Freq')] for data_segment in data]
        stim_rand = [np.random.normal(0, STIM_RANDOM_NOISE, len(v)) for v in vel]

        # build a control response to make sure we'd be able to accurately recover the filter if there was one
        control = [sp_signal.fftconvolve(v, CONTROL_FILTER, 'full') for v in vel]
        control = [c + np.random.normal(0, CONTROL_NOISE, c.shape) for c in control]
        control = [c[:-N_TIMESTEPS_FILTER + 1] for c in control]

        # calculate various cross-correlations (first variable is always "cause", second, "effect")
        n_lags_back = int(round(LAG_BACK / DT))
        n_lags_forward = int(round(LAG_FORWARD / DT))

        vel_x_lmr, p_vel_x_lmr, lb_vel_x_lmr, ub_vel_x_lmr = \
            signal.xcov_simple_two_sided_multi(vel, lmr, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True,
                                               confidence=.95)
        vel_x_lpr, p_vel_x_lpr, lb_vel_x_lpr, ub_vel_x_lpr = \
            signal.xcov_simple_two_sided_multi(vel, lpr, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)
        rand_x_lpr, p_rand_x_lpr, lb_rand_x_lpr, ub_rand_x_lpr = \
            signal.xcov_simple_two_sided_multi(stim_rand, lpr, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)
        vel_x_control, p_vel_x_control, lb_vel_x_control, ub_vel_x_control = \
            signal.xcov_simple_two_sided_multi(vel, control, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)
        vel_x_freq, p_vel_x_freq, lb_vel_x_freq, ub_vel_x_freq = \
            signal.xcov_simple_two_sided_multi(vel, freq, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)
        vel_abs_x_freq, p_vel_abs_x_freq, lb_vel_abs_x_freq, ub_vel_abs_x_freq = \
            signal.xcov_simple_two_sided_multi(vel_abs, freq, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)

        # calculate auto-correlations for different variables
        vel_x_vel, p_vel_x_vel, lb_vel_x_vel, ub_vel_x_vel = \
            signal.xcov_simple_two_sided_multi(vel, vel, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)
        rand_x_rand, p_rand_x_rand, lb_rand_x_rand, ub_rand_x_rand = \
            signal.xcov_simple_two_sided_multi(stim_rand, stim_rand, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)
        lmr_x_lmr, p_lmr_x_lmr, lb_lmr_x_lmr, ub_lmr_x_lmr = \
            signal.xcov_simple_two_sided_multi(lmr, lmr, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)
        lpr_x_lpr, p_lpr_x_lpr, lb_lpr_x_lpr, ub_lpr_x_lpr = \
            signal.xcov_simple_two_sided_multi(lmr, lmr, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)
        freq_x_freq, p_freq_x_freq, lb_freq_x_freq, ub_freq_x_freq = \
            signal.xcov_simple_two_sided_multi(freq, freq, n_lags_back=n_lags_back,
                                               n_lags_forward=n_lags_forward, normed=True)

        t = np.arange(-n_lags_back, n_lags_forward) * DT

        # plot cross-correlations
        fig, axs = plt.subplots(5, 1, sharex=True, tight_layout=True)
        [ax.axhline(0, ls='--') for ax in axs]

        axs[0].plot(t, vel_x_lmr, lw=LW)
        axs[0].fill_between(t, lb_vel_x_lmr, ub_vel_x_lmr, color='b', alpha=ALPHA)

        axs[1].plot(t, vel_x_lpr, lw=LW)
        axs[1].fill_between(t, lb_vel_x_lpr, ub_vel_x_lpr, color='b', alpha=ALPHA)

        axs[2].plot(t, rand_x_lpr, lw=LW)
        axs[2].fill_between(t, lb_rand_x_lpr, ub_rand_x_lpr, color='b', alpha=ALPHA)

        axs[3].plot(t, vel_x_freq, lw=LW)
        axs[3].fill_between(t, lb_vel_x_freq, ub_vel_x_freq, color='b', alpha=ALPHA)

        axs[4].plot(t, vel_abs_x_freq, lw=LW)
        axs[4].fill_between(t, lb_vel_abs_x_freq, ub_vel_abs_x_freq, color='b', alpha=ALPHA)

        axs[0].set_ylabel('vel x lmr')
        axs[1].set_ylabel('vel x lpr')
        axs[2].set_ylabel('rand x lpr')
        axs[3].set_ylabel('vel x freq')
        axs[4].set_ylabel('|vel| x freq')

        axs[3].set_xlabel('t (s)')

        axs[0].set_title('cross-correlations')

        if PLOT_TIME_SERIES:
            # plot time-series
            fig, axs = plt.subplots(6, 1, figsize=FIG_SIZE_TIME_SERIES, sharex=True, tight_layout=True)
            for d_ctr, data_segment in enumerate(data):
                t = data_segment[:, 0]
                axs[0].plot(t, lmr[d_ctr], lw=LW, color='b')
                axs[1].plot(t, lpr[d_ctr], lw=LW, color='b')
                axs[2].plot(t, freq[d_ctr], lw=LW, color='b')
                axs[3].plot(t, vel[d_ctr], lw=LW, color='r')
                axs[4].plot(t, vel_abs[d_ctr], lw=LW, color='r')
                axs[5].plot(t, pos[d_ctr], lw=LW, color='r')
            axs[0].set_ylabel('lmr')
            axs[1].set_ylabel('lpr')
            axs[2].set_ylabel('freq')
            axs[3].set_ylabel('vel')
            axs[4].set_ylabel('vel_abs')
            axs[5].set_ylabel('pos')
            axs[5].set_xlabel('t (s)')
            axs[0].set_title('down-sampled time-series')
            axs[0].set_xlim(data[0][0, 0], data[-1][-1, 0])

        # plot p-values
        if PLOT_P_VALUES:
            fig, axs = plt.subplots(4, 1, sharex=True, tight_layout=True)
            axs[0].plot(t, p_vel_x_lmr)
            #axs[0].plot(t, p_vel_x_control, c='k')
            axs[1].plot(t, p_vel_x_lpr)
            axs[2].plot(t, p_vel_x_freq)
            axs[3].plot(t, p_vel_abs_x_freq)

            [ax.set_ylim(0, 0.1) for ax in axs]

            axs[0].set_ylabel('vel x lmr')
            axs[1].set_ylabel('vel x lpr')
            axs[2].set_ylabel('vel x freq')
            axs[3].set_ylabel('|vel| x freq')

            axs[3].set_xlabel('t (s)')

            axs[0].set_title('p-values')

        # plot auto-correlations
        if PLOT_AUTO_CORRELATIONS:
            fig, axs = plt.subplots(4, 1, sharex=True, tight_layout=True)
            axs[0].plot(t, vel_x_vel)
            axs[1].plot(t, lmr_x_lmr)
            axs[2].plot(t, lpr_x_lpr)
            axs[3].plot(t, freq_x_freq)

            axs[0].set_ylabel('vel')
            axs[1].set_ylabel('lmr')
            axs[2].set_ylabel('lpr')
            axs[3].set_ylabel('freq')

            axs[3].set_xlabel('t (s)')

            axs[0].set_title('auto-correlations')

        plt.show(block=True)


if __name__ == '__main__':
    main()