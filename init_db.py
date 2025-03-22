from app import create_app, db
from app.models import User, Project, Organization
from app.init_resources import init_learning_resources

app = create_app()

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create a test user
        test_user = User(username='test_user', email='test@example.com')
        test_user.set_password('password')
        db.session.add(test_user)
        
        # Create some sample projects
        project1 = Project(
            title='Sample Project 1',
            description='This is a test project',
            category='Web Development',
            tech_stack='Python,Flask,SQLAlchemy',
            github_url='https://github.com/user/project1',
            preview_url='https://project1-demo.com',
            author=test_user
        )
        db.session.add(project1)
        
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

        # Initialize resources
        init_learning_resources()

if __name__ == '__main__':
    init_db()
