import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from multimodel_rag.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Raises 401 if the key is missing or wrong."""
    expected_key = get_settings().api_key

    # compare_digest prevents timing attacks
    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )