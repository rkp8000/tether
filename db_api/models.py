from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Float, DateTime
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

    ignored_segments = relationship("IgnoredSegment", backref='trial')


class Experiment(Base):
    __tablename__ = 'experiment'

    id = Column(String(255), primary_key=True)

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


if __name__ == '__main__':
    Base.metadata.create_all(engine)