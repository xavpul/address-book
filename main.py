from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from haversine import haversine, Unit
import math

from core.db import engine, get_db
from core.models import Address
from core.schemas import AddressCreate, AddressOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Address Book API", lifespan=lifespan)


@app.post("/addresses/", response_model=AddressOut)
async def create_address(payload: AddressCreate, db: AsyncSession = Depends(get_db)):
    addr = Address(name=payload.name, lat=payload.lat, lng=payload.lng)
    db.add(addr)
    await db.flush()
    await db.refresh(addr)
    return AddressOut(id=addr.id, name=addr.name, lat=addr.lat, lng=addr.lng)


@app.get("/addresses/{addr_id}", response_model=AddressOut)
async def read_address(addr_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Address).where(Address.id == addr_id)
    obj = (await db.execute(stmt)).scalars().first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return AddressOut(id=obj.id, name=obj.name, lat=obj.lat, lng=obj.lng)


def _bbox_for_radius(lat: float, lng: float, radius_km: float):
    lat_delta = radius_km / 111.32
    # Guard against cos(lat) ~ 0 near poles
    denom = 111.32 * max(1e-9, math.cos(math.radians(lat)))
    lng_delta = radius_km / denom
    return (lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta)


@app.get("/addresses/nearby", response_model=list[AddressOut])
async def nearby_addresses(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    lat_min, lat_max, lng_min, lng_max = _bbox_for_radius(lat, lng, radius_km)

    stmt = (
        select(Address)
        .where(Address.lat.between(lat_min, lat_max))
        .where(Address.lng.between(lng_min, lng_max))
    )
    candidates = (await db.execute(stmt)).scalars().all()

    center = (lat, lng)
    results = [
        AddressOut(id=a.id, name=a.name, lat=a.lat, lng=a.lng)
        for a in candidates
        if haversine((a.lat, a.lng), center, unit=Unit.KILOMETERS) <= radius_km
    ]
    return results

