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

PLOT_AUTO_CORRELATIONS = False

TRIAL_ID = 18
LAG = 5  # in seconds
DT = .02  # in seconds

CONTROL_FILTER_T = np.linspace(0, LAG, int(LAG/DT), endpoint=False)
CONTROL_FILTER = .1 * np.exp(-CONTROL_FILTER_T / 1.)
CONTROL_SHIFT = 20
CONTROL_FILTER = np.concatenate([np.zeros(20,), CONTROL_FILTER[:-CONTROL_SHIFT]])
CONTROL_NOISE = 0.000001
N_TIMESTEPS_FILTER = len(CONTROL_FILTER)


def main():
    trial = session.query(models.Trial).get(TRIAL_ID)

    data, _, cols, _ = edr_handling.load_from_trial(trial, dt=DT, unwrap_barpos=True)

    pos = [data_segment[:, cols.index('Barpos')] for data_segment in data]
    vel = [np.gradient(pos_segment) / DT for pos_segment in pos]
    vel_abs = [np.abs(vel_segment) for vel_segment in vel]
    lmr = [data_segment[:, cols.index('LmR')] for data_segment in data]
    freq = [data_segment[:, cols.index('Freq')] for data_segment in data]

    # build a control response to make sure we'd be able to accurately recover the filter if there was one
    control = [sp_signal.fftconvolve(v, CONTROL_FILTER, 'full') for v in vel]
    control = [c + np.random.normal(0, CONTROL_NOISE, c.shape) for c in control]
    control = [c[:-N_TIMESTEPS_FILTER + 1] for c in control]

    # calculate various cross-correlations (first variable is always "cause", second, "effect")
    n_lags = int(round(LAG / DT))
    vel_x_lmr, p_vel_x_lmr = signal.xcov_simple_one_sided_multi(vel, lmr, n_lags=n_lags, normed=True)
    vel_x_control, p_vel_x_control = signal.xcov_simple_one_sided_multi(vel, control, n_lags=n_lags, normed=True)
    vel_x_freq, p_vel_x_freq = signal.xcov_simple_one_sided_multi(vel, freq, n_lags=n_lags, normed=True)
    vel_abs_x_freq, p_vel_abs_x_freq = signal.xcov_simple_one_sided_multi(vel_abs, freq, n_lags=n_lags, normed=True)

    # calculate auto-correlations for different variables
    vel_x_vel, p_vel_x_vel = signal.xcov_simple_one_sided_multi(vel, vel, n_lags=n_lags, normed=True)
    lmr_x_lmr, p_lmr_x_lmr = signal.xcov_simple_one_sided_multi(lmr, lmr, n_lags=n_lags, normed=True)
    freq_x_freq, p_freq_x_freq = signal.xcov_simple_one_sided_multi(freq, freq, n_lags=n_lags, normed=True)

    t = np.arange(n_lags) * DT

    # plot cross-correlations
    fig, axs = plt.subplots(3, 1, sharex=True, tight_layout=True)
    axs[0].plot(t, vel_x_lmr)
    axs[0].plot(t, vel_x_control, c='k')
    axs[1].plot(t, vel_x_freq)
    axs[2].plot(t, vel_abs_x_freq)

    axs[0].set_ylabel('vel x lmr')
    axs[1].set_ylabel('vel x freq')
    axs[2].set_ylabel('|vel| x freq')

    axs[2].set_xlabel('t (s)')

    axs[0].set_title('cross-correlations')

    # plot p-values
    fig, axs = plt.subplots(3, 1, sharex=True, tight_layout=True)
    axs[0].plot(t, p_vel_x_lmr)
    axs[0].plot(t, p_vel_x_control, c='k')
    axs[1].plot(t, p_vel_x_freq)
    axs[2].plot(t, p_vel_abs_x_freq)

    [ax.set_ylim(0, 0.1) for ax in axs]

    axs[0].set_ylabel('vel x lmr')
    axs[1].set_ylabel('vel x freq')
    axs[2].set_ylabel('|vel| x freq')

    axs[2].set_xlabel('t (s)')

    axs[0].set_title('p-values')

    # plot auto-correlations
    if PLOT_AUTO_CORRELATIONS:
        fig, axs = plt.subplots(3, 1, sharex=True, tight_layout=True)
        axs[0].plot(t, vel_x_vel)
        axs[1].plot(t, lmr_x_lmr)
        axs[2].plot(t, freq_x_freq)

        axs[0].set_ylabel('vel')
        axs[1].set_ylabel('lmr')
        axs[2].set_ylabel('freq')

        axs[2].set_xlabel('t (s)')

        axs[0].set_title('auto-correlations')

    plt.show(block=True)


if __name__ == '__main__':
    main()