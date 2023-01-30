from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import databases
import sqlalchemy


DATABASE_URL = 'sqlite:///./airports.db'

app = FastAPI()
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

airports = sqlalchemy.Table(
    'airports',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('iata', sqlalchemy.String, unique=True),
    sqlalchemy.Column('airport', sqlalchemy.String, nullable=True)
)


class Airport(BaseModel):
    iata: str
    airport: str


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()


@app.post('/airport/', response_model=Airport)
async def create_airport(airport: Airport):
    query = airports.insert().values(iata=airport.iata, airport=airport.airport)
    last_record_id = await database.execute(query)
    return airport
