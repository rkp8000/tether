"""
Plot the cross-correlations between the following pairs of variables for a specified trial:

velocity vs. left-minus-right
velocity vs. frequency
absolute velocity vs. frequency
"""
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot

from mathmagic import signal

from db_api import models
from db_api.connect import session

import edr_handling

TRIAL_ID = 1
LAG = 2  # in seconds
DT = .02  # in seconds


def main():
    trial = session.query(models.Trial).get(TRIAL_ID)

    data, _, cols, _ = edr_handling.load_from_trial(trial, dt=DT, unwrap_barpos=True)

    pos = data[:, cols.index('Barpos')]
    vel = np.gradient(bar_pos) / DT
    vel_abs = np.abs(vel)
    lmr = data[:, cols.index('LmR')]
    freq = data[:, cols.index('Freq')]

    # calculate various cross-correlations (first variable is always "cause", second, "effect")
    n_lags = int(round(LAG / DT))
    vel_x_lmr = signal.xcov_simple_multi(vel, lmr, n_lags=n_lags, normed=True)
    vel_x_freq = signal.xcov_simple_multi(vel, freq, n_lags=n_lags, normed=True)
    vel_abs_x_freq = vel_x_freq = signal.xcov_simple_multi(vel_abs, freq, n_lags=n_lags, normed=True)

    # calculate auto-correlations for different variables
    vel_x_vel = signal.xcov_simple_multi(vel, vel, n_lags=n_lags, normed=True)
    lmr_x_lmr = signal.xcov_simple_multi(lmr, lmr, n_lags=n_lags, normed=True)
    freq_x_freq = signal.xcov_simple_multi(freq, freq, n_lags=n_lags, normed=True)

    t = np.arange(n_lags) * DT

    # plot cross-correlations
    fig, axs = plt.subplots(3, 1, sharex=True)
    axs[0].plot(t, vel_x_lmr)
    axs[1].plot(t, vel_x_freq)
    axs[2].plot(t, vel_abs_x_freq)

    axs[0].set_ylabel('vel x lmr')
    axs[1].set_ylabel('vel x freq')
    axs[2].set_ylabel('|vel| x freq')

    axs[2].set_xlabel('t (s)')

    # plot auto-correlations
    fig, axs = plt.subplots(3, 1, sharex=True)
    axs[0].plot(t, vel_x_vel)
    axs[1].plot(t, lmr_x_lmr)
    axs[2].plot(t, freq_x_freq)

    axs[0].set_ylabel('vel')
    axs[1].set_ylabel('lmr')
    axs[2].set_ylabel('freq')

plt.show(block=True)