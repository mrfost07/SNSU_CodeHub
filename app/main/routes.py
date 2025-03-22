from flask import render_template, current_app, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.main import bp
from app.models import Project, LearningPath
from app import db
import os
from datetime import datetime

@bp.context_processor
def utility_processor():
    current_year = datetime.now().year
    return {'now': datetime.utcnow(), 'current_year': current_year}

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.index'))
    
    projects = Project.query.filter(
        (Project.title.contains(query)) |
        (Project.description.contains(query)) |
        (Project.tags.contains(query))
    ).all()
    
    learning_paths = LearningPath.query.filter(
        (LearningPath.title.contains(query)) |
        (LearningPath.description.contains(query)) |
        (LearningPath.programming_language.contains(query))
    ).all()
    
    return render_template('main/search.html', 
                         query=query,
                         projects=projects,
                         learning_paths=learning_paths)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Create upload directory if it doesn't exist 
                upload_folder = os.path.join(current_app.root_path, 'static', 'img')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Save the file
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                current_user.profile_picture = filename
                
                try:
                    db.session.commit()
                    flash('Profile picture updated successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('Error updating profile picture', 'error')
                    return redirect(url_for('main.profile'))

        # Handle other profile fields
        current_user.github_username = request.form.get('github_username')
        current_user.skills = request.form.get('skills') 
        current_user.bio = request.form.get('bio')
        current_user.gender = request.form.get('gender')
        current_user.relationship_status = request.form.get('relationship_status')
        current_user.location = request.form.get('location')
        current_user.course = request.form.get('course')
        current_user.organization = request.form.get('organization')
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile', 'error')
        
        return redirect(url_for('main.profile'))
    
    return render_template('main/profile.html', user=current_user)

@bp.route('/')
@bp.route('/index')
def index():
    featured_projects = Project.query.limit(3).all()
    learning_paths = LearningPath.query.limit(3).all()
    return render_template('main/index.html', 
                         projects=featured_projects,
                         learning_paths=learning_paths)

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        user_projects = current_user.projects.all()
        return render_template('main/dashboard.html', projects=user_projects)
    return render_template('main/index.html')
