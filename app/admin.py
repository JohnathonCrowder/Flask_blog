from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort, send_file
from flask_login import login_required, current_user
from .models import db, User, Post, SiteSettings
from functools import wraps
from datetime import datetime, timedelta
from flask import request, url_for
from sqlalchemy import or_
import io

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            flash('You need to be an admin to access this page.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_posts = Post.query.count()
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    new_users_count = User.query.filter(User.created_at >= seven_days_ago).count()
    new_posts_count = Post.query.filter(Post.created_at >= seven_days_ago).count()
    
    draft_posts_count = Post.query.filter_by(status='draft').count()
    new_drafts_count = Post.query.filter(Post.status == 'draft', Post.created_at >= seven_days_ago).count()
    
    categories = db.session.query(Post.category, db.func.count(Post.id)).group_by(Post.category).all()
    categories_count = len(categories)
    popular_category = max(categories, key=lambda x: x[1])[0] if categories else "None"
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_posts=total_posts,
                           new_users_count=new_users_count,
                           new_posts_count=new_posts_count,
                           draft_posts_count=draft_posts_count,
                           new_drafts_count=new_drafts_count,
                           categories_count=categories_count,
                           popular_category=popular_category,
                           recent_users=recent_users,
                           recent_posts=recent_posts)

@admin.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    now = datetime.utcnow()
    return render_template('admin/users.html', 
                          users=users,
                          now=now,
                          timedelta=timedelta)

@admin.route('/admin/posts')
@login_required
@admin_required
def manage_posts():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    author_id = request.args.get('author')
    search = request.args.get('search')

    query = Post.query

    if status:
        query = query.filter(Post.status == status)
    if author_id:
        query = query.filter(Post.user_id == author_id)
    if search:
        query = query.filter(or_(
            Post.title.ilike(f'%{search}%'),
            Post.content.ilike(f'%{search}%')
        ))

    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    authors = User.query.all()

    return render_template('admin/posts.html', posts=posts, authors=authors)

@admin.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def site_settings():
    if request.method == 'POST':
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
        
        # Update settings
        settings.site_name = request.form.get('site_name', '')
        settings.site_description = request.form.get('site_description', '')
        settings.contact_email = request.form.get('contact_email', '')
        settings.posts_per_page = int(request.form.get('posts_per_page', 10))
        settings.maintenance_mode = 'maintenance_mode' in request.form
        settings.allow_registration = 'allow_registration' in request.form
        
        # Social media links
        settings.facebook_url = request.form.get('facebook_url', '')
        settings.twitter_url = request.form.get('twitter_url', '')
        settings.instagram_url = request.form.get('instagram_url', '')
        settings.linkedin_url = request.form.get('linkedin_url', '')

        # SEO settings
        settings.meta_keywords = request.form.get('meta_keywords', '')
        settings.meta_description = request.form.get('meta_description', '')
        
        # Handle OG image
        if request.form.get('remove_og_image') == 'true':
            current_app.logger.info("Removing OG image")
            settings.og_image = None
            settings.og_image_type = None
        elif 'og_image' in request.files:
            file = request.files['og_image']
            if file and file.filename:
                current_app.logger.info(f"Saving new OG image: {file.filename}")
                settings.og_image = file.read()
                settings.og_image_type = file.content_type
                current_app.logger.info(f"Saved image of type: {settings.og_image_type} and size: {len(settings.og_image)} bytes")

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.site_settings'))

    settings = SiteSettings.query.first()
    if settings and settings.og_image:
        current_app.logger.info(f"Settings page loaded with existing OG image of size: {len(settings.og_image)} bytes")
    return render_template('admin/settings.html', settings=settings)

@admin.route('/admin/og-image')
def serve_og_image():
    settings = SiteSettings.query.first()
    if not settings or not settings.og_image:
        current_app.logger.error("No OG image found")
        abort(404)
    current_app.logger.info(f"Serving OG image of type: {settings.og_image_type}")
    return send_file(
        io.BytesIO(settings.og_image),
        mimetype=settings.og_image_type
    )

@admin.route('/admin/test-og-image')
@login_required
@admin_required
def test_og_image():
    settings = SiteSettings.query.first()
    if not settings:
        return jsonify({'error': 'No settings found'})
    
    image_info = {
        'has_image': settings.og_image is not None,
        'image_type': settings.og_image_type,
        'image_size': len(settings.og_image) if settings.og_image else 0
    }
    return jsonify(image_info)

@admin.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Admin status for {user.username} has been updated.", 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} has been deleted.", 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title}' has been deleted.", 'success')
    return redirect(url_for('admin.manage_posts'))