"""
Open Trial 5 and figure out why there is a significant correlation between the lmr behavior and the stimulus that follows it.
"""
from __future__ import division, print_function

TRIAL_ID = 5
DT = .02
LW = 2
ALPHA = .5

FIG_SIZE_TIME_SERIES = (16, 12)

LAG_FORWARD = 5  # in seconds
LAG_BACK = 0.5  # in seconds

import numpy as np
import matplotlib.pyplot as plt
plt.ion()
from scipy import signal as sp_signal

from math_tools import signal
from math_tools import stats

from db_api import models
from db_api.connect import session

import edr_handling


trial = session.query(models.Trial).get(TRIAL_ID)
data, _, cols, _ = edr_handling.load_from_trial(trial, dt=DT, unwrap_barpos=True, lmr_zscore=False)

pos = [data_segment[:, cols.index('Barpos')] for data_segment in data]
vel = [np.gradient(pos_segment) / DT for pos_segment in pos]
vel_abs = [np.abs(vel_segment) for vel_segment in vel]
lmr = [data_segment[:, cols.index('LmR')] for data_segment in data]
lpr = [data_segment[:, cols.index('Lamp')] + data_segment[:, cols.index('Ramp')]
       for data_segment in data]
freq = [data_segment[:, cols.index('Freq')] for data_segment in data]

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
vel_x_freq, p_vel_x_freq, lb_vel_x_freq, ub_vel_x_freq = \
    signal.xcov_simple_two_sided_multi(vel, freq, n_lags_back=n_lags_back,
                                       n_lags_forward=n_lags_forward, normed=True)
vel_abs_x_freq, p_vel_abs_x_freq, lb_vel_abs_x_freq, ub_vel_abs_x_freq = \
    signal.xcov_simple_two_sided_multi(vel_abs, freq, n_lags_back=n_lags_back,
                                       n_lags_forward=n_lags_forward, normed=True)

# plot cross-correlations
fig, axs = plt.subplots(4, 1, sharex=True, tight_layout=True)
[ax.axhline(0, ls='--') for ax in axs]

t = np.arange(-n_lags_back, n_lags_forward) * DT

axs[0].plot(t, vel_x_lmr, lw=LW)
axs[0].fill_between(t, lb_vel_x_lmr, ub_vel_x_lmr, color='b', alpha=ALPHA)

axs[1].plot(t, vel_x_lpr, lw=LW)
axs[1].fill_between(t, lb_vel_x_lpr, ub_vel_x_lpr, color='b', alpha=ALPHA)

axs[2].plot(t, vel_x_freq, lw=LW)
axs[2].fill_between(t, lb_vel_x_freq, ub_vel_x_freq, color='b', alpha=ALPHA)

axs[3].plot(t, vel_abs_x_freq, lw=LW)
axs[3].fill_between(t, lb_vel_abs_x_freq, ub_vel_abs_x_freq, color='b', alpha=ALPHA)

axs[0].set_ylabel('vel x lmr')
axs[1].set_ylabel('vel x lpr')
axs[2].set_ylabel('vel x freq')
axs[3].set_ylabel('|vel| x freq')

axs[3].set_xlabel('t (s)')

axs[0].set_title('cross-correlations')

# plot time-series
if False:
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

plt.draw()

import pdb; pdb.set_trace()