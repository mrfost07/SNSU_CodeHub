import os
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
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
    tags = db.Column(db.String(200))
    github_repo = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

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
    comments = db.relationship('Comment', backref='community_post', lazy='dynamic', 
                             primaryjoin="Comment.post_id == CommunityPost.id",
                             cascade='all, delete-orphan')
    shares = db.relationship('Share', backref='post', lazy='dynamic')

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

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
