from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_AsText
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import engine, get_db
from core.models import Address
from core.schemas import AddressCreate, AddressOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Address Book API",
    lifespan=lifespan,
)


@app.post("/addresses/", response_model=AddressOut)
async def create_address(
    payload: AddressCreate,
    db: AsyncSession = Depends(get_db),
):
    point = WKTElement(f"POINT({payload.lng} {payload.lat})", srid=4326)
    addr = Address(name=payload.name, geom=point)
    db.add(addr)
    await db.flush()
    await db.refresh(addr)
    return addr


@app.get("/addresses/{addr_id}", response_model=AddressOut)
async def read_address(
    addr_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        Address.id,
        Address.name,
        ST_AsText(Address.geom).label("wkt"),
    ).where(Address.id == addr_id)
    row = (await db.execute(stmt)).first()
    if not row:
        raise HTTPException(404, "Not found")
    _, name, wkt = row
    lng, lat = wkt.replace("POINT(", "").rstrip(")").split()
    return AddressOut(
        id=addr_id,
        name=name,
        lat=float(lat),
        lng=float(lng),
    )
