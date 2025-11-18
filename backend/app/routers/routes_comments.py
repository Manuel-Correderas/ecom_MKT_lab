# app/routers/routes_comments.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from ..deps import get_db
from ..models.models import Comment, Product
from ..schemas.comment_schemas import CommentCreate, CommentOut

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("", response_model=list[CommentOut])
def list_comments(
    db: Session = Depends(get_db),
    product_id: Optional[str] = Query(None)
):
    q = db.query(Comment)
    if product_id:
        q = q.filter(Comment.product_id == product_id)
    rows = q.order_by(Comment.created_at.desc()).all()
    return rows

@router.post("", response_model=CommentOut, status_code=201)
def create_comment(payload: CommentCreate, db: Session = Depends(get_db)):
    # Validar producto existente
    p = db.query(Product).filter(Product.id == payload.product_id, Product.is_active == True).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    c = Comment(
        product_id=payload.product_id,
        user_name=payload.user_name or "Anónimo",
        rating=payload.rating,
        criteria=payload.criteria or {},
        comment=payload.comment or ""
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: str, db: Session = Depends(get_db)):
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if not c:
        return
    db.delete(c)
    db.commit()
