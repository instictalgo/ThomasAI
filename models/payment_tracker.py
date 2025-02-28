from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
import datetime

# Import the shared Base
from models.base import Base

class PaymentStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class PaymentMethod(enum.Enum):
    paypal = "paypal"
    crypto_btc = "crypto_btc"
    crypto_eth = "crypto_eth"
    crypto_sol = "crypto_sol"
    bank_transfer = "bank_transfer"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String)
    payment_method = Column(String)
    status = Column(String, default="pending")
    transaction_id = Column(String, nullable=True)
    payment_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert payment object to dictionary"""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "transaction_id": self.transaction_id,
            "payment_link": self.payment_link,
            "created_at": self.created_at.strftime("%Y-%m-%d") if self.created_at else None,
            "completed_at": self.completed_at.strftime("%Y-%m-%d") if self.completed_at else None
        }
