from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename  # Add this import
import os
from .models import db, Post, User

blog = Blueprint('blog', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@blog.route('/blog')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('blog/index.html', posts=posts)

@blog.route('/blog/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog/post.html', post=post)

@blog.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        content = request.form.get('content')
        category = request.form.get('category')
        tags = request.form.get('tags')
        status = request.form.get('status', 'draft')
        
        # Handle image upload
        featured_image = None
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ensure upload directory exists
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                # Save the file
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                featured_image = f'uploads/{filename}'

        post = Post(
            title=title,
            subtitle=subtitle,
            content=content,
            category=category,
            tags=tags,
            status=status,
            featured_image=featured_image,
            author=current_user
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post.id))
    
    return render_template('blog/create.html')

@blog.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.subtitle = request.form.get('subtitle')
        post.content = request.form.get('content')
        post.category = request.form.get('category')
        post.tags = request.form.get('tags')
        post.status = request.form.get('status')
        
        # Handle image upload
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                # Delete old image if it exists
                if post.featured_image:
                    old_filepath = os.path.join(current_app.root_path, 'static', post.featured_image)
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                post.featured_image = f'uploads/{filename}'
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post.id))
    
    return render_template('blog/create.html', post=post)

@blog.route('/blog/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    # Delete featured image if it exists
    if post.featured_image:
        filepath = os.path.join(current_app.root_path, 'static', post.featured_image)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('blog.index'))


@blog.route('/blog/author/<int:user_id>')
def author_profile(user_id):
    author = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=author).order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('blog/author.html', author=author, posts=posts)