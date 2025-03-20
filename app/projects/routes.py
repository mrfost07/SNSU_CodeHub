from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.projects import bp
from app.models import Project
import openai

@bp.route('/projects')
def index():
    projects = Project.query.all()
    return render_template('projects/index.html', projects=projects)

@bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        project = Project(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            tags=request.form['tags'],
            github_repo=request.form['github_repo'],
            author=current_user
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!')
        return redirect(url_for('projects.index'))
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
