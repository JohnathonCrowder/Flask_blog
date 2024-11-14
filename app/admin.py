from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .models import db, User, Post, SiteSettings
from functools import wraps
from datetime import datetime, timedelta
from flask import request, url_for
from sqlalchemy import or_
from datetime import datetime, timedelta



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
    # Get total counts
    total_users = User.query.count()
    total_posts = Post.query.count()

    # Get counts for the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    new_users_count = User.query.filter(User.created_at >= seven_days_ago).count()
    new_posts_count = Post.query.filter(Post.created_at >= seven_days_ago).count()

    # Get recent users and posts
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_posts=total_posts,
                           new_users_count=new_users_count,
                           new_posts_count=new_posts_count,
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

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.site_settings'))

    settings = SiteSettings.query.first()
    return render_template('admin/settings.html', settings=settings)

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