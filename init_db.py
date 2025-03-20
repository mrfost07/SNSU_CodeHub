from app import create_app, db
from app.models import Organization
from app.init_resources import init_learning_resources

def init_organizations():
    app = create_app()
    with app.app_context():
        # Drop existing tables and create new ones
        db.drop_all()
        db.create_all()
        
        # Create organizations
        orgs = [
            {
                'name': 'BSIT',
                'description': 'Bachelor of Science in Information Technology community'
            },
            {
                'name': 'BSCS',
                'description': 'Bachelor of Science in Computer Science community'
            },
            {
                'name': 'BSIS',
                'description': 'Bachelor of Science in Information Systems community'
            },
            {
                'name': 'BSCPE',
                'description': 'Bachelor of Science in Computer Engineering community'
            }
        ]
        
        try:
            for org_data in orgs:
                org = Organization(**org_data)
                db.session.add(org)
            db.session.commit()
            print("Organizations initialized successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing organizations: {e}")

def init_resources():
    app = create_app()
    with app.app_context():
        # Initialize resources
        init_learning_resources()

if __name__ == '__main__':
    init_organizations()
    init_resources()
