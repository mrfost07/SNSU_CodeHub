from app import db
from app.models import LearningResource

def init_learning_resources():
    # List of initial resources
    resources = [
        {
            'title': 'W3Schools Python Tutorial',
            'description': 'Comprehensive Python tutorial covering basics to advanced topics with interactive examples.',
            'resource_type': 'tutorial',
            'url': 'https://www.w3schools.com/python/',
            'thumbnail_url': 'https://www.w3schools.com/images/w3schools_logo_436_2.png',
            'difficulty_level': 'beginner',
            'programming_language': 'Python'
        },
        {
            'title': 'JavaScript Crash Course For Beginners',
            'description': 'Complete JavaScript tutorial for beginners by Traversy Media covering all the basics.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=hdI2bqOjy3c',
            'thumbnail_url': 'https://img.youtube.com/vi/hdI2bqOjy3c/maxresdefault.jpg',
            'difficulty_level': 'beginner',
            'programming_language': 'JavaScript'
        },
        {
            'title': 'freeCodeCamp Full Stack Development Course',
            'description': 'Complete web development bootcamp covering HTML, CSS, JavaScript, React, Node.js, and more.',
            'resource_type': 'course',
            'url': 'https://www.freecodecamp.org/learn/2022/responsive-web-design/',
            'thumbnail_url': 'https://design-style-guide.freecodecamp.org/downloads/fcc_primary_large.png',
            'difficulty_level': 'intermediate',
            'programming_language': 'Web Development'
        },
        {
            'title': 'MDN Web Development Guide',
            'description': 'Mozilla Developer Network comprehensive web development documentation and tutorials.',
            'resource_type': 'documentation',
            'url': 'https://developer.mozilla.org/en-US/docs/Learn',
            'thumbnail_url': 'https://developer.mozilla.org/mdn-social-share.cd6c4a5a.png',
            'difficulty_level': 'intermediate',
            'programming_language': 'Web Development'
        },
        {
            'title': 'Python Django Tutorial',
            'description': 'Complete Django web framework tutorial by Corey Schafer.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=UmljXZIypDc&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p',
            'thumbnail_url': 'https://img.youtube.com/vi/UmljXZIypDc/maxresdefault.jpg',
            'difficulty_level': 'intermediate',
            'programming_language': 'Python'
        },
        {
            'title': 'Git & GitHub Tutorial',
            'description': 'Complete Git and GitHub crash course by Traversy Media.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=SWYqp7iY_Tc',
            'thumbnail_url': 'https://img.youtube.com/vi/SWYqp7iY_Tc/maxresdefault.jpg',
            'difficulty_level': 'beginner',
            'programming_language': 'Git'
        }
    ]

    # Add resources to database
    for resource_data in resources:
        resource = LearningResource(**resource_data)
        db.session.add(resource)
    
    try:
        db.session.commit()
        print("Learning resources initialized successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing resources: {e}")
