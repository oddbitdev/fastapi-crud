import datetime
from typing import List
from sqlalchemy.orm import Session

import app.api.models as models
import app.api.schemas as schemas


class WorkerNotFoundException(Exception):
    pass


class ShiftNotFoundException(Exception):
    pass


class MoreThanOneShiftPerDatException(Exception):
    pass


class ConsecutiveNextDayShiftException(Exception):
    pass


def create_worker(session: Session, worker: schemas.Worker):
    db_worker = models.Worker(id=worker.id, name=worker.name)
    session.add(db_worker)
    session.commit()
    session.refresh(db_worker)

    return db_worker


def delete_worker(session: Session, worker: schemas.Worker):
    session.delete(worker)
    delete_worker_shifts(session, worker.id)
    session.commit()


def delete_worker_shifts(session: Session, worker_id: int):
    worker_shifts = (
        session.query(models.Shift).filter(models.Shift.worker_id == worker_id).all()
    )
    for shift in worker_shifts:
        session.delete(shift)
    session.commit()


def get_worker_by_id(session, worker_id):
    return session.query(models.Worker).filter(models.Worker.id == worker_id).first()


def get_workers(
    session: Session, skip: int = 0, limit: int = 100
) -> List[models.Worker]:
    return session.query(models.Worker).offset(skip).limit(limit).all()


def create_shift(session: Session, shift: schemas.ShiftCreate):
    db_worker = (
        session.query(models.Worker).filter(models.Worker.id == shift.worker_id).first()
    )
    if not db_worker:
        raise WorkerNotFoundException()

    worker_shifts = get_worker_shifts(session, db_worker.id)

    for ws in worker_shifts:
        if shift.date == ws.date:
            raise MoreThanOneShiftPerDatException()
        if (
            shift.date - datetime.timedelta(days=1) == ws.date
            and shift.slot == schemas.Slot.midnight_to_eight
            and ws.slot == schemas.Slot.four_to_midnight
        ) or (
            shift.date + datetime.timedelta(days=1) == ws.date
            and shift.slot == schemas.Slot.four_to_midnight
            and ws.slot == schemas.Slot.midnight_to_eight
        ):
            raise ConsecutiveNextDayShiftException()

    db_shift = models.Shift(worker_id=shift.worker_id, slot=shift.slot, date=shift.date)
    session.add(db_shift)
    session.commit()
    session.refresh(db_shift)

    return db_shift


def get_worker_shifts(session: Session, worker_id: int):
    return (
        session.query(models.Shift)
        .with_entities(models.Shift.date, models.Shift.slot)
        .filter(models.Shift.worker_id == worker_id)
        .all()
    )


def delete_shift(session: Session, shift_id: int):
    shift = session.query(models.Shift).filter(models.Shift.id == shift_id).first()

    if not shift:
        raise ShiftNotFoundException()

    session.delete(shift)
    session.commit()
