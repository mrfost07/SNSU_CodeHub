from flask import render_template, current_app, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.main import bp
from app.models import Project, LearningPath
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
        current_user.github_username = request.form.get('github_username')
        current_user.skills = request.form.get('skills')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
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
