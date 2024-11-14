from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import io
from .models import db, Post, User
from sqlalchemy import or_

blog = Blueprint('blog', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@blog.route('/blog/image/<int:post_id>')
def serve_image(post_id):
    post = Post.query.get_or_404(post_id)
    if not post.featured_image_data:
        abort(404)
    return send_file(
        io.BytesIO(post.featured_image_data),
        mimetype=post.featured_image_mimetype
    )

@blog.route('/blog')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(status='published').order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('blog/index.html', posts=posts)

@blog.route('/blog/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog/post.html', post=post)

@blog.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_administrator():
        abort(403)  # Only admins can create posts
        
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        content = request.form.get('content')
        category = request.form.get('category')
        tags = request.form.get('tags')
        status = request.form.get('status', 'draft')
        
        post = Post(
            title=title,
            subtitle=subtitle,
            content=content,
            category=category,
            tags=tags,
            status=status,
            author=current_user
        )
        
        # Handle image upload
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename and allowed_file(file.filename):
                # Read the file data and mime type
                image_data = file.read()
                mimetype = file.content_type
                
                post.featured_image_data = image_data
                post.featured_image_mimetype = mimetype
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post.id))
    
    return render_template('blog/create.html')

@blog.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    if not current_user.is_administrator():
        abort(403)
    
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.subtitle = request.form.get('subtitle')
        post.content = request.form.get('content')
        post.category = request.form.get('category')
        post.tags = request.form.get('tags')
        post.status = request.form.get('status')
        
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename and allowed_file(file.filename):
                image_data = file.read()
                mimetype = file.content_type
                post.featured_image_data = image_data
                post.featured_image_mimetype = mimetype
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post.id))
    
    return render_template('blog/create.html', 
                          post=post, 
                          is_edit=True,
                          title="Edit Post")

@blog.route('/blog/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    if not current_user.is_administrator():
        abort(403)  # Only admins can delete posts
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('blog.index'))

@blog.route('/blog/author/<int:user_id>')
def author_profile(user_id):
    author = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=author, status='published').order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('blog/author.html', author=author, posts=posts)

# Optional: Add a route for drafts that only admins can see
@blog.route('/blog/drafts')
@login_required
def drafts():
    if not current_user.is_administrator():
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    drafts = Post.query.filter_by(status='draft').order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('blog/drafts.html', posts=drafts)