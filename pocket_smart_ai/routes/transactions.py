from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Transaction, User
from app.schemas import TransactionCreate, TransactionResponse


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == transaction.user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    new_transaction = Transaction(
        user_id=transaction.user_id,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        amount=transaction.amount,
        description=transaction.description
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.get("/{user_id}", response_model=list[TransactionResponse])
def get_transactions(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .all()
    )