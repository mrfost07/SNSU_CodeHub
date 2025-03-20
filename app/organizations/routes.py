from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.organizations import bp
from app.models import Organization, Post, Comment

@bp.route('/organizations')
def index():
    organizations = Organization.query.all()
    return render_template('organizations/index.html', organizations=organizations)

@bp.route('/organizations/<int:id>')
def view(id):
    organization = Organization.query.get_or_404(id)
    posts = organization.posts.order_by(Post.created_at.desc()).all()
    return render_template('organizations/view.html', organization=organization, posts=posts)

@bp.route('/organizations/<int:id>/join')
@login_required
def join(id):
    organization = Organization.query.get_or_404(id)
    if current_user not in organization.members:
        organization.members.append(current_user)
        db.session.commit()
        flash('You have joined the organization!')
    return redirect(url_for('organizations.view', id=id))

@bp.route('/organizations/<int:org_id>/post', methods=['POST'])
@login_required
def create_post(org_id):
    organization = Organization.query.get_or_404(org_id)
    if current_user not in organization.members:
        flash('You must be a member to post')
        return redirect(url_for('organizations.view', id=org_id))
    
    post = Post(
        title=request.form['title'],
        content=request.form['content'],
        post_type=request.form['post_type'],
        author=current_user,
        organization=organization
    )
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('organizations.view', id=org_id))

@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment(
        content=request.form['content'],
        author=current_user,
        post=post
    )
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('organizations.view', id=post.organization_id))

@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user in post.likes:
        post.likes.remove(current_user)
    else:
        post.likes.append(current_user)
    db.session.commit()
    return jsonify({'likes': len(post.likes)})
