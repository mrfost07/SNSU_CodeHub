# SNSU CodeHub

SNSU CodeHub is a collaborative platform designed for developers, students, and coding enthusiasts from Sakon Nakhon Rajabhat University. The platform provides learning resources, project collaboration tools, and a community space for coding education.

## Features

- **Learning Resources**: Curated collection of tutorials, videos, and documentation
- **Project Collaboration**: Work on real projects with peers
- **Community Organizations**: Join department-specific groups (BSIT, BSCS, etc.)
- **Interactive Learning**: Follow structured learning paths
- **Dark Mode Support**: Enhanced UI with dark mode option
- **Responsive Design**: Works on all devices

## Setup

1. Clone the repository:
```bash
git clone https://github.com/mrfost07/SNSU_CodeHub.git
cd SNSU_CodeHub
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
   flask db init
   flask db migrate -m "initial migration"
   flask db upgrade
```

5. Run the development server:
```bash
flask run
```

## Project Structure
![Project Structure](public/screenshots/structure.png)