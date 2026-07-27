"""
Script d'initialisation de la base de données.
Crée : 1 admin, 2 branches, 2 users communs, 4 lignes de stock de test.
 
Usage : depuis le dossier backoffice/ -> python seed.py
Le script est idempotent : si l'admin existe déjà, il ne fait rien
(pour éviter de dupliquer les données si on le lance plusieurs fois).
"""
from app import create_app
from app.extensions import db
from app.models import Branch, Stock, User
 
 
def seed():
    app = create_app()
 
    # app_context() nécessaire car db.session a besoin de savoir
    # à quelle application/config il est rattaché.
    with app.app_context():
        # Crée les tables si elles n'existent pas encore (la factory ne le
        # fait plus, c'est au script d'init de s'en charger).
        db.create_all()
 
        # Vérification d'idempotence : si l'admin existe déjà, on arrête.
        if User.query.filter_by(email="admin@company.com").first():
            print("Déjà initialisé, rien à faire.")
            return
 
        # --- Branches ---
        branch1 = Branch(branch_name="Branch Thonon")
        branch2 = Branch(branch_name="Branch Geneve")
        db.session.add_all([branch1, branch2])
        db.session.commit()  # commit ici pour que branch1.id / branch2.id existent
 
        # --- Admin (branch_id = None : il ne gère pas de stock) ---
        admin = User(email="admin@company.com", is_admin=True, branch_id=None)
        admin.set_password("Hbnt0ry!Adm1n")  # mot de passe temporaire, à changer après le premier login
 
        # --- Users communs, un par branche ---
        user1 = User(
            email="employe.thonon@company.com", is_admin=False, branch_id=branch1.id
        )
        user1.set_password("Th0non!Stock9")
 
        user2 = User(
            email="employe.geneve@company.com", is_admin=False, branch_id=branch2.id
        )
        user2.set_password("Geneve!Stock7")
 
        db.session.add_all([admin, user1, user2])
        db.session.commit()
 
        # --- Stock de test (product_id = identifiants qui viendront de la Product API) ---
        stocks = [
            Stock(branch_id=branch1.id, product_id="prod-001", quantity=50),
            Stock(branch_id=branch1.id, product_id="prod-002", quantity=20),
            Stock(branch_id=branch2.id, product_id="prod-001", quantity=15),
            Stock(branch_id=branch2.id, product_id="prod-003", quantity=30),
        ]
        db.session.add_all(stocks)
        db.session.commit()
 
        print("Base initialisée : 1 admin, 2 branches, 2 users, 4 lignes de stock.")
 
 
if __name__ == "__main__":
    seed()
 