from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.domains.asesores import service
from app.domains.asesores.schemas import (
    AsesorCreate,
    AsesorResponse,
    AsesorUpdate,
    AsignarGrupoRequest,
    CuotaAsesorResponse,
    RegistrarPagoCuotaRequest,
)
from app.domains.usuarios.models import Usuario

router = APIRouter()


# 1. GET /asesores
@router.get("/", response_model=list[AsesorResponse])
def listar_asesores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[AsesorResponse]:
    asesores = service.listar_asesores(db)
    return [service.build_asesor_response(db, a) for a in asesores]


# 2. POST /asesores
@router.post("/", response_model=AsesorResponse, status_code=status.HTTP_201_CREATED)
def crear_asesor(
    data: AsesorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> AsesorResponse:
    asesor = service.crear_asesor(db, data, current_user)
    return service.build_asesor_response(db, asesor)


# 3. GET /asesores/me  ← LITERAL antes que /{asesor_id}
@router.get("/me", response_model=AsesorResponse)
def get_mi_asesor(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> AsesorResponse:
    from app.domains.asesores import repository as repo

    asesor = repo.get_by_usuario_id(db, current_user.id)
    if asesor is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay asesor vinculado a tu usuario",
        )
    return service.build_asesor_response(db, asesor)


# 4. GET /asesores/cuotas  ← LITERAL antes que /{asesor_id}
@router.get("/cuotas", response_model=list[CuotaAsesorResponse])
def listar_cuotas(
    asesor_id: Optional[uuid.UUID] = Query(default=None),
    mes: Optional[int] = Query(default=None),
    anio: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[CuotaAsesorResponse]:
    cuotas = service.listar_cuotas(db, asesor_id=asesor_id, mes=mes, anio=anio)
    return [CuotaAsesorResponse.model_validate(c) for c in cuotas]


# 5. POST /asesores/cuotas/generar  ← LITERAL antes que /{asesor_id}
@router.post("/cuotas/generar", status_code=status.HTTP_200_OK)
def generar_cuotas_mes(
    mes: int = Query(...),
    anio: int = Query(...),
    monto_default: float = Query(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
) -> dict:
    creadas = service.generar_cuotas_mes(db, mes=mes, anio=anio, monto_default=monto_default)
    return {"cuotas_creadas": creadas, "mes": mes, "anio": anio}


# 6. PATCH /asesores/cuotas/{cuota_id}  ← "cuotas" literal ANTES de /{asesor_id}
@router.patch("/cuotas/{cuota_id}", response_model=CuotaAsesorResponse)
def registrar_pago_cuota(
    cuota_id: uuid.UUID,
    data: RegistrarPagoCuotaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> CuotaAsesorResponse:
    cuota = service.registrar_pago_cuota(db, cuota_id, data, current_user)
    return CuotaAsesorResponse.model_validate(cuota)


# 7. GET /asesores/{asesor_id}
@router.get("/{asesor_id}", response_model=AsesorResponse)
def obtener_asesor(
    asesor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> AsesorResponse:
    asesor = service.obtener_asesor_or_404(db, asesor_id)
    return service.build_asesor_response(db, asesor)


# 8. PATCH /asesores/{asesor_id}
@router.patch("/{asesor_id}", response_model=AsesorResponse)
def actualizar_asesor(
    asesor_id: uuid.UUID,
    data: AsesorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> AsesorResponse:
    asesor = service.actualizar_asesor(db, asesor_id, data, current_user)
    return service.build_asesor_response(db, asesor)


# 9. DELETE /asesores/{asesor_id}
@router.delete("/{asesor_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def desactivar_asesor(
    asesor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> None:
    service.desactivar_asesor(db, asesor_id, current_user)


# 10. POST /asesores/{asesor_id}/grupos
@router.post("/{asesor_id}/grupos", status_code=status.HTTP_201_CREATED)
def asignar_grupo(
    asesor_id: uuid.UUID,
    data: AsignarGrupoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    ag = service.asignar_grupo(db, asesor_id, data.grupo_id, current_user)
    return {"id": str(ag.id), "asesor_id": str(ag.asesor_id), "grupo_id": str(ag.grupo_id)}


# 11. DELETE /asesores/{asesor_id}/grupos/{grupo_id}
@router.delete("/{asesor_id}/grupos/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def remover_grupo(
    asesor_id: uuid.UUID,
    grupo_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> None:
    service.remover_grupo(db, asesor_id, grupo_id, current_user)


# 12. GET /asesores/{asesor_id}/cuotas
@router.get("/{asesor_id}/cuotas", response_model=list[CuotaAsesorResponse])
def listar_cuotas_asesor(
    asesor_id: uuid.UUID,
    mes: Optional[int] = Query(default=None),
    anio: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[CuotaAsesorResponse]:
    service.obtener_asesor_or_404(db, asesor_id)
    cuotas = service.listar_cuotas(db, asesor_id=asesor_id, mes=mes, anio=anio)
    return [CuotaAsesorResponse.model_validate(c) for c in cuotas]
