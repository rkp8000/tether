from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from connect import engine

Base = declarative_base()


class Trial(Base):
    __tablename__ = 'trial'

    id = Column(Integer, primary_key=True)

    file_name = Column(String(255))
    recording_start = Column(DateTime)
    recording_duration = Column(Float)

    experiment_id = Column(String(255), ForeignKey('experiment.id'))
    insect_id = Column(String(255), ForeignKey('insect.id'))
    pair_id = Column(String(13), ForeignKey('trial_pair.id'))

    ignored_segments = relationship("IgnoredSegment", backref='trial')


class Experiment(Base):
    __tablename__ = 'experiment'

    id = Column(String(255), primary_key=True)
    description = Column(Text)

    directory_path = Column(String(255))

    trials = relationship("Trial", backref='experiment')


class Insect(Base):
    __tablename__ = 'insect'

    id = Column(String(255), primary_key=True)

    trials = relationship("Trial", backref='insect')


class IgnoredSegment(Base):
    __tablename__ = 'ignored_segment'

    id = Column(Integer, primary_key=True)

    start_time = Column(Float)
    end_time = Column(Float)
    trial_id = Column(Integer, ForeignKey('trial.id'))


class TrialPair(Base):
    __tablename__ = 'trial_pair'

    id = Column(String(13), primary_key=True)

    trials = relationship("Trial", backref='pair')


class TrialOdorStatus(Base):
    __tablename__ = 'trial_odor_status'

    id = Column(Integer, primary_key=True)
    trial_id = Column(Integer, ForeignKey('trial.id'))

    solenoid_active = Column(Boolean)
    odor = Column(String(100))

    trial = relationship("Trial", backref='odor_status', uselist=False)


if __name__ == '__main__':
    Base.metadata.create_all(engine)