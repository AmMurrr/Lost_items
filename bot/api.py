import os
from datetime import date
from json import JSONDecodeError
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

if API_URL is None:
    raise RuntimeError("API_URL неизвестен")


class ApiClientError(Exception):
    """Если API недоступен или возвращает ошибку."""


class ApiNotFoundError(ApiClientError):
    """Если API вернул 404."""


async def search_items(
    description: str,
    station: str,
    loss_date: date,
) -> list[dict[str, Any]]:
    payload = {
        "description": description,
        "station": station,
        "loss_date": loss_date.isoformat(),
    }

    url = f"{API_URL.rstrip('/')}/search"

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ApiClientError(
            f"API returned HTTP {exc.response.status_code}"
        ) from exc
    except httpx.HTTPError as exc:
        raise ApiClientError("API is unavailable") from exc

    try:
        data = response.json()
    except JSONDecodeError as exc:
        raise ApiClientError("API returned invalid JSON") from exc

    if not isinstance(data, list):
        raise ApiClientError("API returned unexpected response")

    return data


async def get_item(item_id: int) -> dict[str, Any]:
    url = f"{API_URL.rstrip('/')}/items/{item_id}"

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise ApiNotFoundError("Item not found") from exc

        raise ApiClientError(
            f"API returned HTTP {exc.response.status_code}"
        ) from exc
    except httpx.HTTPError as exc:
        raise ApiClientError("API is unavailable") from exc

    try:
        data = response.json()
    except JSONDecodeError as exc:
        raise ApiClientError("API returned invalid JSON") from exc

    if not isinstance(data, dict):
        raise ApiClientError("API returned unexpected response")

    return data

