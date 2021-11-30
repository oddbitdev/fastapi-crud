from sqlalchemy import Date, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    shifts = relationship("Shift", back_populates="workers")


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey('workers.id'))
    slot = Column(Integer)
    date = Column(Date)

    workers = relationship("Worker", back_populates="shifts")
