from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import re


Base = declarative_base()

app = FastAPI()


class Airport(Base):
    __tablename__ = 'airports'
    id = Column(Integer, primary_key=True)
    iata = Column(String, unique=True, nullable=False)
    airport = Column(String, nullable=True)


class AirportIn(BaseModel):
    iata: str
    airport: str

    @validator('iata')
    def iata_must_be_3_symbols(cls, value):
        if len(value) != 3:
            raise ValueError('IATA must be 3 symbols long')

        if not bool(re.fullmatch(r'[a-zA-Z]+', value)):
            raise ValueError('IATA must contain only symbols')

        return value.upper()

    re.fullmatch(r'[a-zA-Z]+', 'AAA')


engine = create_engine('sqlite:///./airports.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@app.post('/airports/')
async def create_airport(airport: AirportIn):
    db = SessionLocal()

    try:
        new_airport = Airport(iata=airport.iata, airport=airport.airport)
        db.add(new_airport)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return {'message': 'Airport created'}


@app.get('/airports/{iata}')
async def read_airport(iata: str):
    db = SessionLocal()
    airport = db.query(Airport).filter(Airport.iata == iata.upper()).first()
    db.close()

    if airport is None:
        raise HTTPException(status_code=404, detail='Airport not found')

    return airport


@app.put('/airports/{airport_id}')
async def update_airport(airport_id: str, airport: AirportIn):
    db = SessionLocal()
    db_airport = db.query(Airport).get(airport_id)

    if db_airport is None:
        raise HTTPException(status_code=404, detail='Airport not found')

    airport_with_same_iata = db.query(Airport).filter(Airport.iata == airport.iata).first()

    if airport_with_same_iata is not None and airport_id != airport_with_same_iata.id:
        raise HTTPException(status_code=400, detail="An airport with the same iata '{}' already exists".format(airport.iata))

    db_airport.iata = airport.iata
    db_airport.airport = airport.airport

    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

    return {'message': 'Airport updated'}


@app.delete("/airports/{airport_id}")
async def delete_airport(airport_id: int):
    db = SessionLocal()
    db_airport = db.query(Airport).get(airport_id)

    if db_airport is None:
        raise HTTPException(status_code=404, detail="Airport not found")

    db.delete(db_airport)
    db.commit()
    db.close()

    return {'message': 'Airport deleted'}
