# backend/app/routers/routes_admin.py

from datetime import datetime, date, time, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel   # 👈 ESTE ES EL IMPORT QUE FALTABA

from sqlalchemy.orm import Session, joinedload

from ..deps import get_db
from ..models.models import User, Order, Payment
from ..schemas.admin_schemas import AdminUserOut, AdminOrderOut

try:
    from ..security import require_admin
    AdminDep = Depends(require_admin)
except ImportError:
    AdminDep = Depends(get_db)


router = APIRouter(prefix="/admin", tags=["admin"])


# ==============
#   USUARIOS
# ==============
@router.get("/users", response_model=List[AdminUserOut])
def list_users(
    estado: str | None = Query(None, description="ACTIVO / REVISION / BLOQUEADO"),
    solo_nuevos: bool = Query(False),
    dias: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    admin=AdminDep,  # para que sólo admin pueda pegarle
):
    q = db.query(User)

    if estado:
        q = q.filter(User.estado == estado)

    if solo_nuevos:
        corte = datetime.utcnow() - timedelta(days=dias)
        q = q.filter(User.creado_en >= corte)

    q = q.order_by(User.creado_en.desc())
    return q.all()


class EstadoUpdate(BaseModel):
    estado: str  # ACTIVO / REVISION / BLOQUEADO


@router.patch("/users/{user_id}/estado")
def update_user_estado(
    user_id: str,
    payload: EstadoUpdate,
    db: Session = Depends(get_db),
    admin=AdminDep,
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if payload.estado not in ("ACTIVO", "REVISION", "BLOQUEADO"):
        raise HTTPException(status_code=400, detail="Estado inválido")

    user.estado = payload.estado
    db.commit()
    db.refresh(user)
    return {"ok": True, "id": user.id, "estado": user.estado}


class DniBlockUpdate(BaseModel):
    dni_bloqueado: bool


@router.patch("/users/{user_id}/dni-block")
def update_user_dni_block(
    user_id: str,
    payload: DniBlockUpdate,
    db: Session = Depends(get_db),
    admin=AdminDep,
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.dni_bloqueado = 1 if payload.dni_bloqueado else 0
    db.commit()
    db.refresh(user)
    return {"ok": True, "id": user.id, "dni_bloqueado": bool(user.dni_bloqueado)}


# ==============
#   ÓRDENES
# ==============
@router.get("/orders", response_model=List[AdminOrderOut])
def list_orders(
    from_date: date,
    to_date: date,
    db: Session = Depends(get_db),
    admin=AdminDep,
):
    # incluir el día "hasta" completo
    start_dt = datetime.combine(from_date, time.min)
    end_dt = datetime.combine(to_date + timedelta(days=1), time.min)

    orders = (
        db.query(Order)
        .filter(Order.created_at >= start_dt, Order.created_at < end_dt)
        .options(joinedload(Order.payments))
        .all()
    )

    results: list[AdminOrderOut] = []

    for o in orders:
        # Tomamos el último pago como estado "principal"
        payment: Payment | None = None
        if o.payments:
            payment = sorted(o.payments, key=lambda p: p.created_at)[-1]

        payment_status = payment.status if payment else None
        tx_ref = payment.tx_ref if payment else None

        # Buscar email de usuario si está ligado
        user_email = None
        if o.user_id:
            user_email = db.query(User.email).filter(User.id == o.user_id).scalar()

        results.append(
            AdminOrderOut(
                id=o.id,
                created_at=o.created_at,
                user_id=o.user_id,
                user_email=user_email,
                total_amount=o.total_amount,
                payment_status=payment_status,
                tx_ref=tx_ref,
            )
        )

    return results
