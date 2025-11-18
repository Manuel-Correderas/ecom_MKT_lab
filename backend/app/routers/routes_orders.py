# backend/app/routers/routes_orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from ..deps import get_db, get_current_user
from ..models.models import Cart, CartItem, Order, OrderItem, User  # ajustá si cambia el nombre del modelo

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderItemOut(BaseModel):
    product_id: str
    name: str
    price: int
    qty: int

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: str
    user_id: str
    total: int
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


@router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 1) Buscar carrito del usuario
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == user.id)
        .order_by(Cart.created_at.desc())
        .first()
    )

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    # 2) Calcular total
    total = sum(item.price * item.qty for item in cart.items)

    if total <= 0:
        raise HTTPException(status_code=400, detail="Total inválido")

    # 3) Crear la orden
    order = Order(
        user_id=user.id,
        total=total,
        status="paid",  # o "pending" si querés simular pasarela
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # 4) Crear los items de la orden
    for ci in cart.items:
        oi = OrderItem(
            order_id=order.id,
            product_id=ci.product_id,
            name=ci.name,
            price=ci.price,
            qty=ci.qty,
        )
        db.add(oi)

    # 5) Vaciar carrito
    for ci in list(cart.items):
        db.delete(ci)

    db.commit()
    db.refresh(order)

    # 6) Mapear a salida
    items_out = [
        OrderItemOut(
            product_id=oi.product_id,
            name=oi.name,
            price=oi.price,
            qty=oi.qty,
        )
        for oi in order.items
    ]

    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        total=order.total,
        items=items_out,
    )
