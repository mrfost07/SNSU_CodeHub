from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.learning import bp
from app.models import LearningPath, Tutorial, LearningResource
import openai
from app.init_resources import init_learning_resources

@bp.route('/learning')
def index():
    paths = LearningPath.query.all()
    return render_template('learning/index.html', paths=paths)

@bp.route('/learning/<int:path_id>')
def view_path(path_id):
    path = LearningPath.query.get_or_404(path_id)
    return render_template('learning/path.html', path=path)

@bp.route('/api/ai/code-review', methods=['POST'])
@login_required
def ai_code_review():
    code = request.json.get('code')
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=f"Review this code:\n{code}\n\nCode review:",
        max_tokens=150
    )
    return jsonify({'review': response.choices[0].text})

@bp.route('/api/ai/suggest-path', methods=['POST'])
@login_required
def suggest_learning_path():
    skills = request.json.get('skills')
    goals = request.json.get('goals')
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=f"Suggest a learning path for someone with skills in {skills} who wants to learn {goals}",
        max_tokens=200
    )
    return jsonify({'suggestion': response.choices[0].text})

@bp.route('/resources')
def resources():
    resources = LearningResource.query.order_by(LearningResource.created_at.desc()).all()
    if not resources:
        # Initialize resources if none exist
        init_learning_resources()
        resources = LearningResource.query.order_by(LearningResource.created_at.desc()).all()
    return render_template('learning/resources.html', resources=resources)

@bp.route('/resources/<int:id>')
def view_resource(id):
    resource = LearningResource.query.get_or_404(id)
    return render_template('learning/resource_detail.html', resource=resource)

@bp.route('/resources/add', methods=['GET', 'POST'])
@login_required
def add_resource():
    if request.method == 'POST':
        resource = LearningResource(
            title=request.form['title'],
            description=request.form['description'],
            resource_type=request.form['resource_type'],
            url=request.form['url'],
            thumbnail_url=request.form['thumbnail_url'],
            difficulty_level=request.form['difficulty_level'],
            programming_language=request.form['programming_language'],
            user_id=current_user.id,
            learning_path_id=request.form.get('learning_path_id')
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource added successfully!', 'success')
        return redirect(url_for('learning.resources'))
    
    learning_paths = LearningPath.query.all()
    return render_template('learning/add_resource.html', learning_paths=learning_paths)
