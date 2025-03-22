from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.projects import bp
from app.models import Project
import openai
from werkzeug.utils import secure_filename
import os
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGE_SIZE = (800, 400)  # Maximum width and height for project images

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_project_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure upload directory exists
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'projects')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Open and resize image using PIL
        image = Image.open(file)
        image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        filepath = os.path.join(upload_dir, filename)
        image.save(filepath)
        return filename
    return None

@bp.route('/projects')
def index():
    projects = Project.query.all()
    return render_template('projects/index.html', projects=projects)

@bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            # Handle image upload
            image_filename = None
            if 'project_image' in request.files:
                file = request.files['project_image']
                image_filename = save_project_image(file)

            # Get the tech stack as a list and join with commas
            tech_stack = ','.join(request.form.getlist('tech_stack'))
            
            project = Project(
                title=request.form['title'],
                description=request.form['description'],
                category=request.form['category'],
                tech_stack=tech_stack,
                github_url=request.form['github_url'],
                preview_url=request.form['preview_url'],
                image=image_filename,  # Add this line
                author=current_user
            )
            db.session.add(project)
            db.session.commit()
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects.view', id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating project: {str(e)}', 'error')
            return redirect(url_for('projects.create'))
            
    return render_template('projects/create.html')

@bp.route('/projects/<int:id>')
def view(id):
    project = Project.query.get_or_404(id)
    return render_template('projects/view.html', project=project)

@bp.route('/projects/<int:id>/ai-analyze', methods=['POST'])
@login_required
def ai_analyze_project(id):
    project = Project.query.get_or_404(id)
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=f"Analyze this project:\nTitle: {project.title}\nDescription: {project.description}\nTags: {project.tags}",
        max_tokens=200
    )
    return jsonify({'analysis': response.choices[0].text})

@bp.route('/projects/recommend', methods=['GET'])
@login_required
def recommend_projects():
    user_skills = current_user.skills
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=f"Recommend projects for a developer with skills in: {user_skills}",
        max_tokens=150
    )
    return jsonify({'recommendations': response.choices[0].text})

@bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    if current_user.id != project.author_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        # Delete project image if it exists
        if project.image:
            image_path = os.path.join(current_app.root_path, 'static', 'uploads', 'projects', project.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(project)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    project = Project.query.get_or_404(id)
    if current_user.id != project.author_id:
        flash('You can only edit your own projects.', 'error')
        return redirect(url_for('projects.view', id=id))
        
    if request.method == 'POST':
        try:
            # Handle image upload
            if 'project_image' in request.files:
                file = request.files['project_image']
                if file.filename:
                    # Delete old image if it exists
                    if project.image:
                        old_image_path = os.path.join(current_app.root_path, 'static', 'uploads', 'projects', project.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    # Save new image
                    image_filename = save_project_image(file)
                    if image_filename:
                        project.image = image_filename

            # Update other fields
            project.title = request.form['title']
            project.description = request.form['description']
            project.category = request.form['category']
            project.tech_stack = ','.join(request.form.getlist('tech_stack'))
            project.github_url = request.form['github_url']
            project.preview_url = request.form['preview_url']
            
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects.view', id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'error')
            
    return render_template('projects/edit.html', project=project)
