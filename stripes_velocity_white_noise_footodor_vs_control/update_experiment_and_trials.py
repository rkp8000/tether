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

EXPERIMENT_ID = 'stripes_velocity_white_noise_footodor_vs_control'
EXPERIMENT_DESCRIPTION = 'Mosquitoes were flown in the flight arena for two six minute trials. In the first trial only a striped velocity white noise visual stimulus was presented. In the second trial the visual stimulus continued and a series of odor pulses was injected into the airstream. In the control case the odor was clean air and in the experimental case the odor was odor collected from my feet on glass beads.'
EXPERIMENT_DIRECTORY_PATH = 'experiments/stripes_velocity_white_noise_footodor_vs_control'
DATETIME_EXPRESSION = '(\d{6}_\d{6})_stripes'
INSECT_NUMBER_EXPRESSION = 'insect(\d*)_'
ODOR_TYPE_EXPRESSION = '_(\w*)_ypos'
SOLENOID_STATUS_EXPRESSION = '_odor_(\S*).EDR'

ARENA_DATA_DIRECTORY = os.getenv('ARENA_DATA_DIRECTORY')


def main():
    # get or create experiment
    experiment = get_or_create(session, models.Experiment,
                               id=EXPERIMENT_ID,
                               description=EXPERIMENT_DESCRIPTION,
                               directory_path=EXPERIMENT_DIRECTORY_PATH)

    full_directory_path = os.path.join(ARENA_DATA_DIRECTORY, EXPERIMENT_DIRECTORY_PATH)

    edr_file_names = [file_name for file_name in os.listdir(full_directory_path)
                      if file_name.lower().endswith('.edr')]

    # get all trials and add them to database
    for file_name in edr_file_names:
        print('Attempting to load file "{}"'.format(file_name))

        # skip if file already added
        if session.query(models.Trial).filter_by(file_name=file_name).all():
            print('Skipping file "{}" because it is already in the database.'.format(file_name))
            continue

        try:
            file_path = os.path.join(full_directory_path, file_name)
            _, recording_start, _, header = edr_handling.load_edr(file_path)
            recording_duration = header['recording_duration']

            # get datetime for trial pair id using regex
            trial_pair_id = re.findall(DATETIME_EXPRESSION, file_name)[0]

            # get or create trial pair
            trial_pair = get_or_create(session, models.TrialPair, id=trial_pair_id)

            # get odor
            odor = re.findall(ODOR_TYPE_EXPRESSION, file_name)[0]

            # get solenoid status
            if re.findall(SOLENOID_STATUS_EXPRESSION, file_name)[0] == 'off':
                solenoid_active = False
            else:
                solenoid_active = True

            odor_status = models.TrialOdorStatus(odor=odor, solenoid_active=solenoid_active)
            session.add(odor_status)

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
            trial.odor_status = odor_status
            trial.pair = trial_pair

            session.add(trial)

        except Exception, e:
            print('Error: "{}"'.format(e))

    session.commit()


if __name__ == '__main__':
    main()