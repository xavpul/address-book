import math

import pytest


@pytest.mark.asyncio
async def test_create_and_get_by_id(client):
    # Create
    payload = {"name": "Home", "lat": 40.7128, "lng": -74.006}
    resp = await client.post("/addresses/", json=payload)
    assert resp.status_code == 200, resp.text
    created = resp.json()
    assert created["id"] >= 1
    assert created["name"] == "Home"
    assert created["lat"] == payload["lat"]
    assert created["lng"] == payload["lng"]

    addr_id = created["id"]

    # Read by id
    resp2 = await client.get(f"/addresses/{addr_id}")
    assert resp2.status_code == 200, resp2.text
    read = resp2.json()
    assert read == created


@pytest.mark.asyncio
async def test_nearby(client):
    # Seed a few points around a center
    center = {"name": "Center", "lat": 37.7749, "lng": -122.4194}  # SF
    a = {"name": "Near1", "lat": 37.7790, "lng": -122.4194}  # ~0.45 km
    b = {"name": "Near2", "lat": 37.7840, "lng": -122.4094}  # ~1.1 km
    c = {"name": "Far", "lat": 37.8044, "lng": -122.2712}  # Oakland, ~13 km

    for p in [center, a, b, c]:
        r = await client.post("/addresses/", json=p)
        assert r.status_code == 200, r.text

    # 1 km radius should include Center and Near1, likely exclude Near2 and Far
    resp = await client.get(
        "/addresses/nearby",
        params={"lat": center["lat"], "lng": center["lng"], "radius_km": 1.0},
    )
    assert resp.status_code == 200, resp.text
    items = resp.json()
    names = {x["name"] for x in items}
    assert "Center" in names
    assert "Near1" in names
    assert "Near2" not in names
    assert "Far" not in names

    # 2 km radius should include Near2
    resp2 = await client.get(
        "/addresses/nearby",
        params={"lat": center["lat"], "lng": center["lng"], "radius_km": 2.0},
    )
    assert resp2.status_code == 200, resp2.text
    names2 = {x["name"] for x in resp2.json()}
    assert "Near2" in names2
    assert "Far" not in names2


@pytest.mark.asyncio
async def test_not_found(client):
    resp = await client.get("/addresses/999999")
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Not found"
