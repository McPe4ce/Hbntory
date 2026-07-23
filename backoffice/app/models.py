import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class BaseModel():
    """BaseModel class that adds logs, and save method"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Save method used in other classes to add a timestamps and in the db"""
        self.updated_at = datetime.now()
        # db.session.add(self)
        #db.session.commit()


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

    """stores the scrypt hash"""
    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    """Deletes a user when called"""
    def deactivate(self):
        self.is_active = False
        self.deleted_at = datetime.now()
        self.save()


class Branch(BaseModel):
    def __init__(self, branch_name):
        super().__init__()
        self.branch_name = branch_name

    