from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask import current_app, jsonify, flash
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.community import bp
from app.models import CommunityPost, Comment, Share, User
from PIL import Image
import io
from sqlalchemy import desc

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}
MAX_IMAGE_SIZE = (800, 800)  # Maximum width and height for images

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(file_storage):
    # Read the image file
    image = Image.open(file_storage)
    
    # Convert RGBA to RGB if necessary
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Resize image while maintaining aspect ratio
    image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or 'JPEG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

@bp.route('/')
@login_required
def index():
    # Get posts with sorting options
    sort = request.args.get('sort', 'recent')
    if (sort == 'popular'):
        posts = CommunityPost.query.join(CommunityPost.likes).\
            group_by(CommunityPost.id).\
            order_by(db.func.count(User.id).desc()).all()
    else:
        posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    
    # Get active users (active in last 24 hours)
    day_ago = datetime.utcnow() - timedelta(days=1)
    active_users = User.query.join(CommunityPost).\
        filter(CommunityPost.created_at >= day_ago).\
        distinct().limit(5).all()
    
    return render_template('community/index.html', 
                         title='Community',
                         posts=posts,
                         active_users=active_users)

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
                
                # Check if it's an image file
                if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # Resize image
                    img_bytes = resize_image(file)
                    
                    # Save the resized image
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    with open(filepath, 'wb') as f:
                        f.write(img_bytes.getvalue())
                else:
                    # For non-image files (like videos), save directly
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
        content = request.json.get('content')
        
        if not content or len(content.strip()) == 0:
            return jsonify({'error': 'Comment cannot be empty'}), 400

        comment = Comment(
            content=content,
            author=current_user,
            post=post
        )
        
        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.username,
                'author_image': comment.author.profile_image,
                'created_at': comment.created_at.strftime('%B %d, %Y %H:%M'),
                'can_delete': current_user.id == comment.author_id,
                'like_count': comment.like_count()
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/post/<int:post_id>/share', methods=['POST'])
@login_required
def share_post(post_id):
    try:
        original_post = CommunityPost.query.get_or_404(post_id)
        
        # If it's a shared post, get the original
        post_to_share = original_post.get_original_post()
        
        # Check if user already shared this post
        existing_share = CommunityPost.query.filter_by(
            author=current_user,
            original_post=post_to_share,
            is_shared=True
        ).first()
        
        if existing_share:
            return jsonify({'error': 'You have already shared this post'}), 400
        
        # Create new shared post
        shared_post = CommunityPost(
            content=post_to_share.content,
            content_type=post_to_share.content_type,
            media_url=post_to_share.media_url,
            author=current_user,
            is_shared=True,
            original_post=post_to_share
        )
        
        db.session.add(shared_post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post shared successfully!',
            'post_id': shared_post.id,
            'shares': post_to_share.share_count()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error sharing post: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    try:
        post = CommunityPost.query.get_or_404(post_id)
        
        # Check if current user is the author
        if current_user.id != post.author_id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Delete the post
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Post deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        if current_user in comment.likes:
            comment.likes.remove(current_user)
            action = 'unliked'
        else:
            comment.likes.append(current_user)
            action = 'liked'
        db.session.commit()
        return jsonify({
            'likes': comment.like_count(),
            'action': action
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        if current_user.id not in [comment.author_id, comment.post.author_id]:
            return jsonify({'error': 'Unauthorized'}), 403
            
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_to_comment(comment_id):
    try:
        parent_comment = Comment.query.get_or_404(comment_id)
        content = request.json.get('content')
        
        if not content or len(content.strip()) == 0:
            return jsonify({'error': 'Reply cannot be empty'}), 400
            
        reply = Comment(
            content=content,
            author=current_user,
            post=parent_comment.post,
            parent=parent_comment
        )
        
        db.session.add(reply)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'reply': {
                'id': reply.id,
                'content': reply.content,
                'author': reply.author.username,
                'author_image': reply.author.profile_image,
                'created_at': reply.created_at.strftime('%B %d, %Y %H:%M')
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
