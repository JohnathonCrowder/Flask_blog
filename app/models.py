from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_administrator(self):
        return self.is_admin

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(500))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')
    featured_image_data = db.Column(db.LargeBinary)  # For storing the actual image data
    featured_image_mimetype = db.Column(db.String(32))  # For storing the image type
    images = db.relationship('PostImage', backref='post', lazy=True, cascade='all, delete-orphan')

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []
    

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
    # Add relationships
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    
class PostImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    image_data = db.Column(db.LargeBinary)
    image_mimetype = db.Column(db.String(32))
    caption = db.Column(db.String(200))
    position = db.Column(db.Integer)  # To maintain image order
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='My Blog')
    site_description = db.Column(db.Text, default='A simple blog website')
    contact_email = db.Column(db.String(120))
    posts_per_page = db.Column(db.Integer, default=10)
    maintenance_mode = db.Column(db.Boolean, default=False)
    allow_registration = db.Column(db.Boolean, default=True)
    
    # Social media links
    facebook_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(200))

    # Meta settings
    meta_keywords = db.Column(db.String(200))
    meta_description = db.Column(db.String(200))
    og_image = db.Column(db.LargeBinary)
    og_image_type = db.Column(db.String(32))