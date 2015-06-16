"""
Created on Fri Mar 27 14:35:44 2015

@author: rkp

Connect to tether or test_tether database.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_CXN = True

if TEST_CXN:
    print 'CONNECTED TO TETHER TEST DATABASE'
    engine = create_engine(os.environ['TEST_TETHER_DB_CXN_URL'])
else:
    print 'CONNECTED TO TETHER PRODUCTION DATABASE'
    x = raw_input('Are you sure you want to connect to the production database [y or n]?')
    if x.lower() == 'y':
        engine = create_engine(os.environ['TETHER_DB_CXN_URL'])
    else:
        raise RuntimeError('User prevented write access to database.')

engine.connect()

Session = sessionmaker(bind=engine)
session = Session()