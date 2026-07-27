import uuid
from datetime import datetime
 
from werkzeug.security import check_password_hash, generate_password_hash
 
from app.extensions import db
 
 
class BaseModel(db.Model):
    """BaseModel class that adds logs, and save method"""
    __abstract__ = True
 
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
 
    def save(self):
        """Save method used in other classes to add a timestamps and in the db"""
        self.updated_at = datetime.now()
        db.session.add(self)
        db.session.commit()
 
 
class User(BaseModel):
    """A backoffice user, belonging to one branch."""
    __tablename__ = "users"
 
    email = db.Column(db.String(120), nullable=False, unique=True)
    branch_id = db.Column(db.String(36), db.ForeignKey("branches.id"), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
 
    branch = db.relationship("Branch", back_populates="users")
 
    def __init__(self, email, branch_id, is_admin=False):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.email = email
        self.branch_id = branch_id
        self.is_admin = is_admin
        self.is_active = True
        self.deleted_at = None
        self.password_hash = None
 
    def set_password(self, raw_password):
        """stores the scrypt hash"""
        self.password_hash = generate_password_hash(raw_password)
 
    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
 
    def deactivate(self):
        """Deactivate a user when called"""
        if not self.is_active:
            return
        self.is_active = False
        self.deleted_at = datetime.now()
        self.save()
 
 
class Branch(BaseModel):
    """An object that will hold different backoffice users and products"""
    __tablename__ = "branches"
 
    branch_name = db.Column(db.String(100), nullable=False, unique=True)
 
    users = db.relationship("User", back_populates="branch")
    stocks = db.relationship("Stock", back_populates="branch")
 
    def __init__(self, branch_name):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.branch_name = branch_name
 
 
class Stock(BaseModel):
    """Represents the quantity of a product in a branch"""
    __tablename__ = "stocks"
 
    product_id = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    branch_id = db.Column(db.String(36), db.ForeignKey("branches.id"), nullable=False)
 
    branch = db.relationship("Branch", back_populates="stocks")
 
    __table_args__ = (
        db.CheckConstraint("quantity >= 0", name="quantity_non_negative"),
    )
 
    def __init__(self, product_id, quantity, branch_id):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.product_id = product_id
        self.quantity = quantity
        self.branch_id = branch_id
 
    def add_stock(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.quantity += amount
        self.save()
        return self.quantity
 
    def remove_stock(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.quantity:
            raise ValueError("not enough stock")
        self.quantity -= amount
        self.save()
        return self.quantity
 
    def consult_stock(self):
        return self.quantity
 