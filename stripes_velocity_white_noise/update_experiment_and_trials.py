"""
Make sure experiment is in database, and update to include any new trials.
"""
from __future__ import print_function, division

import os
import re
import datetime

from db_api.connect import session
from db_api import models
from db_api import get_or_create

import edr_handling

EXPERIMENT_ID = 'stripes_velocity_white_noise_no_odor'
EXPERIMENT_DIRECTORY_PATH = 'experiments/stripes_velocity_white_noise_no_odor'
INSECT_NUMBER_EXPRESSION = 'insect(\d*)_'

ARENA_DATA_DIRECTORY = os.getenv('ARENA_DATA_DIRECTORY')


def main():
    # get or create experiment
    experiment = get_or_create(session, models.Experiment,
                               id=EXPERIMENT_ID,
                               directory_path=EXPERIMENT_DIRECTORY_PATH)

    full_directory_path = os.path.join(ARENA_DATA_DIRECTORY, EXPERIMENT_DIRECTORY_PATH)

    edr_files = [file_name for file_name in os.listdir(full_directory_path)
                 if file_name.lower().endswith('.edr')]

    # get all trials and add them to database
    for file_name in edr_files:
        print('Attempting to load file "{}"'.format(file_name))

        # skip if file already added
        if session.query(models.Trial).filter_by(file_name=file_name).first():
            print('Skipping file "{}" because it is already in the database.'.format(file_name))
            continue

        try:
            file_path = os.path.join(full_directory_path, file_name)
            _, recording_start, _, header = edr_handling.load_edr(file_path)
            recording_duration = header['recording_duration']

            # get insect number from file name using regex
            insect_number = re.findall(INSECT_NUMBER_EXPRESSION, file_name)[0]

            insect_id = '{}_{}'.format(recording_start.strftime('%Y%m%d'), insect_number)

            # get/create insect
            insect = get_or_create(session, models.Insect, id=insect_id)

            trial = models.Trial(file_name=file_name,
                                 recording_start=recording_start,
                                 recording_duration=recording_duration)

            trial.insect = insect
            trial.experiment = experiment

            session.add(trial)

        except Exception, e:
            print('Error: "{}"'.format(e))

    session.commit()


if __name__ == '__main__':
    main()