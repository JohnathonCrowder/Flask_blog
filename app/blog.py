from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import io
from .models import db, Post, User
from sqlalchemy import or_, func

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
    
    # Base query
    query = Post.query
    
    # If user is not admin, only show published posts
    if not current_user.is_authenticated or not current_user.is_administrator():
        query = query.filter_by(status='published')
    
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('blog/index.html', posts=posts)

@blog.route('/blog/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # If the post is a draft and the user is not an admin, return 404
    if post.status != 'published' and (
        not current_user.is_authenticated or 
        not current_user.is_administrator()
    ):
        abort(404)
    
    # Fetch random related posts
    related_posts = Post.query.filter(
        Post.id != post_id,
        Post.status == 'published'
    ).order_by(func.random()).limit(3).all()
    
    return render_template('blog/post.html', post=post, related_posts=related_posts)

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
                image_data = file.read()
                mimetype = file.content_type
                post.featured_image_data = image_data
                post.featured_image_mimetype = mimetype
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post.id))
    
    return render_template('blog/create.html')

# For editing posts
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
        
        # Handle image upload
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename and allowed_file(file.filename):
                post.featured_image_data = file.read()
                post.featured_image_mimetype = file.content_type
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.post', post_id=post.id))
    
    return render_template('blog/create.html', 
                          post=post, 
                          is_edit=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

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
    
    # Base query
    query = Post.query.filter_by(author=author)
    
    # If user is not admin, only show published posts
    if not current_user.is_authenticated or not current_user.is_administrator():
        query = query.filter_by(status='published')
    
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('blog/author.html', author=author, posts=posts)

@blog.route('/blog/drafts')
@login_required
def drafts():
    if not current_user.is_administrator():
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    drafts = Post.query.filter_by(status='draft').order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('blog/drafts.html', posts=drafts)

# Optional: Add a search route
@blog.route('/blog/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        base_query = Post.query.filter(
            or_(
                Post.title.ilike(f'%{query}%'),
                Post.content.ilike(f'%{query}%'),
                Post.tags.ilike(f'%{query}%')
            )
        )
        
        # If user is not admin, only show published posts in search results
        if not current_user.is_authenticated or not current_user.is_administrator():
            base_query = base_query.filter_by(status='published')
        
        search_results = base_query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    else:
        search_results = None
    
    return render_template('blog/search.html', 
                          query=query,
                          results=search_results)