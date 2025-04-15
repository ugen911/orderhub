from fastapi import APIRouter
from .service import get_nomenklatura_full

router = APIRouter()


@router.get("/nomenklatura/{kod}")
def get_nomenklatura_detail(kod: str):
    try:
        return get_nomenklatura_full(kod)
    except Exception as e:
        return {"error": str(e)}
