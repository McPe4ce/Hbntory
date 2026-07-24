import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class BaseModel():
    """BaseModel class that adds logs, and save method"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Save method used in other classes to add a timestamps and in the db"""
        self.updated_at = datetime.now()
        db.session.add(self)
        db.session.commit()


class User(BaseModel):
    """A backoffice user, belonging to one branch."""
    def __init__(self, email, branch_id, is_admin=False):
        super().__init__()
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
    def __init__(self, branch_name):
        super().__init__()
        self.branch_name = branch_name


class Stock(BaseModel):
    """Represents the quantity of a product in a branch"""
    def __init__(self, product_id, quantity, branch_id):
        super().__init__()
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
        