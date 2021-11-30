from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

import app.api.crud as crud
import app.api.models as models
from app.database import SessionLocal, engine
import app.api.schemas as schemas

models.Base.metadata.create_all(bind=engine)
planning_router = APIRouter()


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@planning_router.get("/")
def root():
    return "planning app v 0.1"


@planning_router.post(
    "/workers", response_model=schemas.Worker, status_code=status.HTTP_201_CREATED
)
def create_worker(worker: schemas.Worker, session: Session = Depends(get_session)):
    db_worker = crud.get_worker_by_id(session, worker_id=worker.id)

    if db_worker:
        raise HTTPException(status_code=400, detail="Worker already exists.")

    return crud.create_worker(session, worker=worker)


@planning_router.delete("/workers/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worker(id: int, session: Session = Depends(get_session)):
    db_worker = crud.get_worker_by_id(session, worker_id=id)

    if db_worker:
        crud.delete_worker(session, db_worker)
    else:
        raise HTTPException(status_code=404, detail=f"Worker with id {id} not found")

    return None


@planning_router.get("/workers", response_model=List[schemas.Worker])
def get_all_workers(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return crud.get_workers(session, skip=skip, limit=limit)


@planning_router.get("/workers/{id}", response_model=schemas.Worker)
def get_worker_by_id(id: int, session: Session = Depends(get_session)):
    db_worker = crud.get_worker_by_id(session, worker_id=id)

    if not db_worker:
        raise HTTPException(status_code=404, detail=f"Worker with id {id} not found")

    return db_worker


@planning_router.post(
    "/shifts", response_model=schemas.Shift, status_code=status.HTTP_201_CREATED
)
def create_worker_shift(
    shift: schemas.ShiftCreate, session: Session = Depends(get_session)
):
    try:
        db_shift = crud.create_shift(session, shift)
    except crud.WorkerNotFoundException:
        raise HTTPException(
            status_code=404, detail=f"Worker with id {shift.worker_id} not found"
        )
    except crud.MoreThanOneShiftPerDatException:
        raise HTTPException(
            status_code=400, detail=f"Worker already has a shift for {shift.date}"
        )
    except crud.ConsecutiveNextDayShiftException:
        if shift.slot == schemas.Slot.midnight_to_eight:
            raise HTTPException(
                status_code=400,
                detail="Worker has a shift on the previous day from 16 to 24, leading to two consecutive shifts",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Worker has a shift on the next day from 0 to 8, leading to two consecutive shifts",
            )
    else:
        return db_shift


@planning_router.delete("/shifts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shift(id: int, session: Session = Depends(get_session)):
    try:
        crud.delete_shift(session, id)
    except crud.ShiftNotFoundException:
        raise HTTPException(status_code=404, detail=f"Shift with id {id} not found")
    else:
        return None


@planning_router.get("/shifts/worker/{worker_id}", response_model=List[schemas.ShiftResponse])
def get_worker_shifts(worker_id: int, session: Session = Depends(get_session)):
    db_worker = crud.get_worker_by_id(session, worker_id=worker_id)

    if not db_worker:
        raise HTTPException(status_code=404, detail=f"Worker with id {worker_id} not found")

    return crud.get_worker_shifts(session, worker_id)


@planning_router.delete("/shifts/worker/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worker_shifts(worker_id: int, session: Session = Depends(get_session)):
    db_worker = crud.get_worker_by_id(session, worker_id=worker_id)

    if not db_worker:
        raise HTTPException(status_code=404, detail=f"Worker with id {worker_id} not found")

    crud.delete_worker_shifts(session, worker_id)
