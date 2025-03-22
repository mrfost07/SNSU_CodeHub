import os
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app, url_for
from datetime import datetime

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    github_username = db.Column(db.String(64))
    skills = db.Column(db.String(500))
    projects = db.relationship('Project', backref='author', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    profile_picture = db.Column(db.String(200), default='default-avatar.png')
    bio = db.Column(db.Text)
    gender = db.Column(db.String(20))
    relationship_status = db.Column(db.String(20))
    location = db.Column(db.String(100))
    course = db.Column(db.String(50))
    organization = db.Column(db.String(100))

    @property
    def profile_image(self):
        """Return the URL for the user's profile image."""
        if not self.profile_picture or self.profile_picture == 'default-avatar.png':
            return url_for('static', filename='img/default-avatar.png')
        
        img_path = os.path.join(current_app.static_folder, 'img', self.profile_picture)
        if os.path.exists(img_path):
            return url_for('static', filename=f'img/{self.profile_picture}')
        return url_for('static', filename='img/default-avatar.png')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    tech_stack = db.Column(db.String(500))  # Comma-separated list of technologies
    github_url = db.Column(db.String(500))
    preview_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.String(500))  # Add this line for project image
    
    @property
    def image_url(self):
        """Return the URL for the project's image."""
        if not self.image:
            return url_for('static', filename='img/default-project.png')
        return url_for('static', filename=f'uploads/projects/{self.image}')

    def get_tech_stack_list(self):
        """Return tech stack as a list"""
        return [tech.strip() for tech in self.tech_stack.split(',')] if self.tech_stack else []

class LearningPath(db.Model):
    __tablename__ = 'learning_path'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    programming_language = db.Column(db.String(50))
    difficulty_level = db.Column(db.String(20))
    tutorials = db.relationship('Tutorial', backref='learning_path', lazy='dynamic')

class Tutorial(db.Model):
    __tablename__ = 'tutorial'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    order = db.Column(db.Integer)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_path.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningResource(db.Model):
    __tablename__ = 'learning_resource'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(50))  # video, article, book, etc.
    url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    programming_language = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_path.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., BSIT, BSCS, etc.
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('User', secondary='organization_members', backref='organizations')
    posts = db.relationship('Post', backref='organization', lazy='dynamic')

# Association table for organization members
organization_members = db.Table('organization_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
    db.Column('role', db.String(20), default='member')
)

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(20))  # idea, bug, announcement, discussion
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    comments = db.relationship('Comment', backref='organization_post', lazy='dynamic', 
                             primaryjoin="Comment.organization_post_id == Post.id",
                             cascade='all, delete-orphan')
    likes = db.relationship('User', secondary='post_likes', backref='liked_posts')

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'))
    organization_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # For replies
    
    # Add relationships
    post = db.relationship('CommunityPost', back_populates='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    likes = db.relationship('User', secondary='comment_likes', backref='liked_comments')
    
    def like_count(self):
        return len(self.likes)

class CommunityPost(db.Model):
    __tablename__ = 'community_post'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)  # Made nullable to allow media-only posts
    content_type = db.Column(db.String(20), default='text')  # text, image, video
    media_url = db.Column(db.String(500))  # URL for image/video content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    
    # Relationships
    author = db.relationship('User', backref='community_posts')
    likes = db.relationship('User', secondary='community_post_likes', backref='liked_community_posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')
    shares = db.relationship('Share', backref='post', lazy='dynamic')
    
    # Add these new fields
    is_shared = db.Column(db.Boolean, default=False)
    original_post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'))
    original_post = db.relationship('CommunityPost', remote_side=[id], 
                                  backref=db.backref('shared_posts', lazy='dynamic'))

    def comment_count(self):
        """Get total number of comments including replies"""
        total_comments = len(self.comments)
        for comment in self.comments:
            total_comments += len(comment.replies)
        return total_comments

    def share_count(self):
        # Count direct shares of this post
        direct_shares = self.shared_posts.count()
        
        # If this is a shared post, include shares from original
        if self.is_shared and self.original_post:
            return self.original_post.share_count()
        return direct_shares

    def get_original_post(self):
        """Get the original post if this is a shared post"""
        if self.is_shared and self.original_post:
            return self.original_post
        return self
    
    def like_count(self):
        """Get total number of likes"""
        return len(self.likes)

    def get_original_post_author(self):
        """Safely get original post author username"""
        if self.original_post and self.original_post.author:
            return self.original_post.author.username
        return "[Deleted User]"

    def get_original_post_content(self):
        """Safely get original post content"""
        if self.original_post:
            return self.original_post.content
        return "[This post has been deleted by the creator]"

    def is_original_post_deleted(self):
        """Check if original post is deleted"""
        return self.is_shared and not self.original_post

class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    created_by = db.relationship('User', backref='created_groups')
    members = db.relationship('User', secondary='group_members', backref='joined_groups')
    posts = db.relationship('CommunityPost', backref='group', lazy='dynamic')

# Association table for group members
group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

class Share(db.Model):
    __tablename__ = 'share'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'))

# Association tables
community_post_likes = db.Table('community_post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('community_post.id'))
)

# Association table for post likes
post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

# Add new association table for comment likes
comment_likes = db.Table('comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
