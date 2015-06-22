"""
Functions for working with edr files.
"""
from __future__ import print_function, division

import os
import datetime
import numpy as np
from scipy.stats import zscore
from math_tools import signal

HEADER_BLOCK_SIZE = 2048
BARPOS_CONVERSION = 360 / 5  # from volts to degrees

DATA_DIRECTORY = os.getenv('ARENA_DATA_DIRECTORY')


def load_edr(file_name, header_block_size=HEADER_BLOCK_SIZE, dt=.01,
             lmr_zscore=True, barpos_in_degrees=True):
    """Load header info and data from binary file."""

    if file_name[-4:].lower() != '.edr':
        raise ValueError('file_name must end with \'.edr\'')

    header = {}

    with open(file_name, 'rb') as f:

        # read header data
        end_of_header = False
        while not end_of_header:

            # read next line
            line = f.readline().rstrip()

            # stop if we've moved beyond the header
            if f.tell() <= header_block_size:
                # get key and value of line as correct type
                key, val = line.split('=')

                try:
                    header[key] = int(val)
                except ValueError:
                    try:
                        header[key] = float(val)
                    except ValueError:
                        header[key] = val
            else:
                end_of_header = True

        # get column names
        cols = [header['YN%d'%ii] for ii in range(header['NC'])]

        # get normalization constants from header
        ad = float(header['AD'])
        adcmax = float(header['ADCMAX'] + 1)

        # move to start of binary data
        f.seek(header_block_size)

        # load data into array
        ncols = header['NC']
        nrows = header['NP']/ncols
        data = np.fromfile(f, dtype=np.int16).reshape((nrows, ncols))
        data = data.astype(float)
        # normalize data by calibration, etc.
        for channel in range(ncols):
            ych_channel = 'YCF%d' % channel
            data[:, channel] *= (float(ad) / (adcmax * header[ych_channel]))

        # add time as first column
        time = np.arange(data.shape[0])[:, None] * header['DT']
        data = np.concatenate([time, data], axis=1)
        cols = ['time'] + cols

        # swap frequency & LmR columns
        cols[3], cols[4] = cols[4], cols[3]
        data[:, [3, 4]] = data[:, [4, 3]]

        # downsample data
        if dt > header['DT']:
            downsample_factor = dt/header['DT']
            idxs = np.round(np.arange(data.shape[0], step=downsample_factor))
            idxs = idxs.astype(int)
            if idxs[-1] == data.shape[0]:
                idxs = idxs[:-1]
            data = data[idxs, :]

    if lmr_zscore:
        lampz = zscore(data[:, cols.index('Lamp')])
        rampz = zscore(data[:, cols.index('Ramp')])
        data[:, cols.index('LmR')] = lampz - rampz

    if barpos_in_degrees:
        barpos = data[:, cols.index('Barpos')] * BARPOS_CONVERSION
        barpos[barpos > 180] -= 360
        data[:, cols.index('Barpos')] = barpos

    # create datetime object for file start time
    dt_format = '%m-%d-%Y %I:%M:%S %p'
    file_start_str = header['CTIME']
    file_start = datetime.datetime.strptime(file_start_str, dt_format)

    # store number of timepoints in header
    header['n_timepoints'] = int(nrows)

    # store recording duration in header
    header['recording_duration'] = int(nrows) * header['DT']

    return data, file_start, cols, header


def load_from_trial(trial, dt=0, lmr_zscore=True, barpos_in_degrees=True, min_seg_lenth=10, unwrap_barpos=False):
    """
    Load an edr file from a trial, splitting it into segments as indicated by
    trial.ignored_segments.

    :param trial: trial data model
    :param dt: time interval for discretization (if down-sampling is desired)
    :param lmr_zscore: set to True to return difference of zscores
    :param barpos_in_degrees: set to True to return bar position in degrees
    :param min_seg_length: minimum number of time points that must be in a segment
    :param unwrap_barpos: set to True to return bar position "un-modded"; useful for calculating bar velocity
    :return: list of 2D arrays, with rows indicating time points and columns variables,
             file start datetime,
             column names,
             edr file header,
    """

    experiment_directory_path = os.path.join(DATA_DIRECTORY, trial.experiment.directory_path)
    file_path = os.path.join(experiment_directory_path, trial.file_name)

    data, file_start, cols, header = load_edr(file_path, dt=dt,
                                              lmr_zscore=lmr_zscore,
                                              barpos_in_degrees=barpos_in_degrees)

    t = data[:, 0]  # get time vector
    n_timesteps = len(t)

    # get indices of ignored segments

    ignored_segments_idx = []
    for i_s in trial.ignored_segments:
        start_time_idx = np.sum(t < i_s.start_time)
        end_time_idx = np.sum(t < i_s.end_time)

        start_time_idx = min(start_time_idx, n_timesteps - 1)
        end_time_idx = min(end_time_idx, n_timesteps - 1)

        ignored_segments_idx += [(start_time_idx, end_time_idx)]

    # get indices of segments to keep
    kept_segments_idx = []
    for k_s_ctr in range(len(ignored_segments_idx) + 1):
        if k_s_ctr == 0:
            start_idx = 0
        else:
            start_idx = ignored_segments_idx[k_s_ctr - 1][1]

        if k_s_ctr == len(ignored_segments_idx):
            end_idx = n_timesteps
        else:
            end_idx = ignored_segments_idx[k_s_ctr][0]

        kept_segments_idx += [(start_idx, end_idx)]

    # return segments of data as long as they are long enough
    data = [data[s[0]:s[1]] for s in kept_segments_idx if (s[1] - s[0]) >= min_seg_lenth]

    if unwrap_barpos:
        for data_segment in data:
            original_barpos = data_segment[:, cols.index('Barpos')]
            data_segment[:, cols.index('Barpos')] = signal.unmod(original_barpos, range=360)

    return data, file_start, cols, header