import pytest
import pytest_asyncio
from datetime import date, timedelta
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from app.db import Base, get_session
from app.main import app

@pytest_asyncio.fixture()
async def client() -> AsyncClient:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()
    await engine.dispose()

def valid_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "Анна Иванова",
        "phone": "+79991234567",
        "booking_date": (date.today() + timedelta(days=1)).isoformat(),
        "booking_time": "19:00:00",
        "guests": 4,
    }
    payload.update(overrides)
    return payload

@pytest.mark.asyncio()
async def test_create_booking_returns_created_booking(client: AsyncClient) -> None:
    response = await client.post("/bookings", json=valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["status"] == "active"
    assert body["name"] == "Анна Иванова"

@pytest.mark.asyncio()
async def test_create_booking_rejects_invalid_payload(client: AsyncClient) -> None:
    response = await client.post(
        "/bookings",
        json=valid_payload(phone="79991234567", guests=13),
    )

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio()
async def test_create_booking_rejects_taken_slot(client: AsyncClient) -> None:
    payload = valid_payload()
    first_response = await client.post("/bookings", json=payload)
    second_response = await client.post(
        "/bookings",
        json=valid_payload(name="Мария Петрова"),
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Booking slot is already taken"}


@pytest.mark.asyncio()
async def test_list_bookings_can_be_filtered_by_date(client: AsyncClient) -> None:
    target_date = (date.today() + timedelta(days=2)).isoformat()
    other_date = (date.today() + timedelta(days=3)).isoformat()
    await client.post("/bookings", json=valid_payload(booking_date=target_date))
    await client.post(
        "/bookings",
        json=valid_payload(
            name="Мария Петрова",
            booking_date=other_date,
            booking_time="20:00:00",
        ),
    )

    response = await client.get("/bookings", params={"date": target_date})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["booking_date"] == target_date


@pytest.mark.asyncio()
async def test_get_booking_by_id_and_not_found(client: AsyncClient) -> None:
    created = await client.post("/bookings", json=valid_payload())
    booking_id = created.json()["id"]

    found_response = await client.get(f"/bookings/{booking_id}")
    missing_response = await client.get("/bookings/999")

    assert found_response.status_code == 200
    assert found_response.json()["id"] == booking_id
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "Booking not found"}


@pytest.mark.asyncio()
async def test_cancel_booking_keeps_record_and_frees_slot(client: AsyncClient) -> None:
    payload = valid_payload()
    created = await client.post("/bookings", json=payload)
    booking_id = created.json()["id"]

    cancel_response = await client.delete(f"/bookings/{booking_id}")
    recreate_response = await client.post(
        "/bookings",
        json=valid_payload(name="Мария Петрова"),
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"
    assert recreate_response.status_code == 201