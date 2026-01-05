from shopyo_auth.models import Role, User
from init import db
from app import create_app

app = create_app()

with app.app_context():
    # Create roles
    client_role = Role.query.filter_by(name="client").first()
    if not client_role:
        client_role = Role(name="client")
        db.session.add(client_role)
        db.session.commit()
        print("Created role: client")
    
    # Assign to user (demo user)
    user = User.query.first()
    if user:
        if client_role not in user.roles:
            user.roles.append(client_role)
            db.session.commit()
            print(f"Assigned 'client' role to user: {user.email}")
        else:
            print(f"User {user.email} already has 'client' role")
    else:
        print("No users found. Run 'shopyo initialise' first.")
