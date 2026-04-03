from fastapi import APIRouter

router = APIRouter()


@router.get("/hash/{sha256}")
def hash_lookup(sha256: str) -> dict:
    return {"sha256": sha256, "known": False, "message": "DB dedup lookup not connected yet"}
