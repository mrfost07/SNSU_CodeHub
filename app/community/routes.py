from datetime import datetime  # Make sure this is the first import
import os
from werkzeug.utils import secure_filename
from flask import current_app, jsonify, flash
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.community import bp
from app.models import CommunityPost, Comment, Share, User

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@login_required
def index():
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    return render_template('community/index.html', title='Community', posts=posts)

@bp.route('/discussions')
@login_required
def discussions():
    return render_template('community/discussions.html', title='Discussions')

@bp.route('/members')
@login_required
def members():
    return render_template('community/members.html', title='Community Members')

@bp.route('/post/create', methods=['POST'])
@login_required
def create_post():
    try:
        content = request.form.get('content')
        content_type = 'text'
        media_url = None

        if 'media' in request.files:
            file = request.files['media']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Ensure upload directory exists
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                media_url = url_for('static', filename=f'uploads/{filename}')
                content_type = 'image' if file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'} else 'video'

        post = CommunityPost(
            content=content,
            content_type=content_type,
            media_url=media_url,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('community.index'))
    except Exception as e:
        flash(f'Error creating post: {str(e)}', 'error')
        return redirect(url_for('community.index'))

@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    try:
        post = CommunityPost.query.get_or_404(post_id)
        content = request.form.get('content')
        
        if not content or len(content.strip()) == 0:
            flash('Comment cannot be empty', 'error')
            return redirect(url_for('community.index'))

        comment = Comment(
            content=content,
            author=current_user,
            post=post,
            created_at=datetime.utcnow()  # This should now work correctly
        )
        
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding comment: {str(e)}', 'error')
        
    return redirect(url_for('community.index'))

@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    if current_user in post.likes:
        post.likes.remove(current_user)
        action = 'unliked'
    else:
        post.likes.append(current_user)
        action = 'liked'
    db.session.commit()
    return jsonify({
        'likes': len(post.likes),
        'action': action
    })

@bp.route('/post/<int:post_id>/share', methods=['POST'])
@login_required
def share_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    share = Share(user_id=current_user.id, post_id=post.id)
    db.session.add(share)
    db.session.commit()
    return jsonify({
        'shares': post.shares.count(),
        'message': 'Post shared successfully!'
    })
