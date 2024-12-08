from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort, send_file
from flask_login import login_required, current_user
from .models import db, User, Post, SiteSettings, Comment
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import or_
import io

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            flash('You need to be an admin to access this page.', 'error')
            return redirect(url_for('auth.login'))
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

    total_comments = Comment.query.count()
    new_comments_count = Comment.query.filter(Comment.created_at >= seven_days_ago).count()
    flagged_comments_count = Comment.query.filter_by(is_flagged=True).count()
    
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
                          recent_posts=recent_posts,
                          total_comments=total_comments,
                          new_comments_count=new_comments_count,
                          flagged_comments_count=flagged_comments_count)

@admin.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    now = datetime.utcnow()
    return render_template('admin/users.html', users=users, now=now, timedelta=timedelta)

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

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'html': render_template('admin/posts_table.html', posts=posts),
            'has_prev': posts.has_prev,
            'has_next': posts.has_next,
            'page': posts.page,
            'total_pages': posts.pages
        })

    return render_template('admin/posts.html', posts=posts, authors=authors)

@admin.route('/admin/comments')
@login_required
@admin_required
def manage_comments():
    page = request.args.get('page', 1, type=int)
    filter_by = request.args.get('filter', 'all')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'newest')

    # Base query
    query = Comment.query

    # Apply filters
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if filter_by == 'today':
        query = query.filter(Comment.created_at >= today_start)
    elif filter_by == 'week':
        week_ago = now - timedelta(days=7)
        query = query.filter(Comment.created_at >= week_ago)
    elif filter_by == 'flagged':
        query = query.filter(Comment.is_flagged == True)

    # Apply search
    if search:
        query = query.filter(Comment.content.ilike(f'%{search}%'))

    # Apply sorting
    if sort_by == 'oldest':
        query = query.order_by(Comment.created_at.asc())
    else:  # newest
        query = query.order_by(Comment.created_at.desc())

    # Debug print
    print("\nDebug: Query results")
    results = query.all()
    for comment in results:
        print(f"Comment: {comment.content}, Created: {comment.created_at}")

    # Pagination
    comments = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('admin/comments.html',
                         comments=comments,
                         current_filter=filter_by,
                         current_sort=sort_by,
                         search_query=search)

@admin.route('/admin/comment/<int:comment_id>/toggle-flag', methods=['POST'])
@login_required
@admin_required
def toggle_flag_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.is_flagged = not comment.is_flagged
    db.session.commit()
    return jsonify({'success': True, 'is_flagged': comment.is_flagged})

@admin.route('/admin/comments/bulk-action', methods=['POST'])
@login_required
@admin_required
def bulk_action_comments():
    action = request.form.get('action')
    comment_ids = request.form.getlist('comment_ids[]')
    
    if not comment_ids:
        flash('No comments selected.', 'error')
        return redirect(url_for('admin.manage_comments'))
    
    comments = Comment.query.filter(Comment.id.in_(comment_ids)).all()
    
    if action == 'delete':
        for comment in comments:
            db.session.delete(comment)
    elif action == 'flag':
        for comment in comments:
            comment.is_flagged = True
    elif action == 'unflag':
        for comment in comments:
            comment.is_flagged = False
    
    db.session.commit()
    flash(f'Bulk action completed on {len(comments)} comments.', 'success')
    return redirect(url_for('admin.manage_comments'))

@admin.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has been deleted.', 'success')
    return redirect(url_for('admin.manage_comments'))

@admin.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def site_settings():
    if request.method == 'POST':
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
        
        settings.site_name = request.form.get('site_name', '')
        settings.site_description = request.form.get('site_description', '')
        settings.contact_email = request.form.get('contact_email', '')
        settings.posts_per_page = int(request.form.get('posts_per_page', 10))
        settings.maintenance_mode = 'maintenance_mode' in request.form
        settings.allow_registration = 'allow_registration' in request.form
        
        settings.facebook_url = request.form.get('facebook_url', '')
        settings.twitter_url = request.form.get('twitter_url', '')
        settings.instagram_url = request.form.get('instagram_url', '')
        settings.linkedin_url = request.form.get('linkedin_url', '')

        settings.meta_keywords = request.form.get('meta_keywords', '')
        settings.meta_description = request.form.get('meta_description', '')
        
        if request.form.get('remove_og_image') == 'true':
            settings.og_image = None
            settings.og_image_type = None
        elif 'og_image' in request.files:
            file = request.files['og_image']
            if file and file.filename:
                settings.og_image = file.read()
                settings.og_image_type = file.content_type

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.site_settings'))

    settings = SiteSettings.query.first()
    return render_template('admin/settings.html', settings=settings)

@admin.route('/admin/og-image')
def serve_og_image():
    settings = SiteSettings.query.first()
    if not settings or not settings.og_image:
        abort(404)
    return send_file(
        io.BytesIO(settings.og_image),
        mimetype=settings.og_image_type
    )

@admin.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash("You cannot change your own admin status.", 'error')
        return redirect(url_for('admin.manage_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Admin status for {user.username} has been updated.", 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash("You cannot delete your own account.", 'error')
        return redirect(url_for('admin.manage_users'))
    
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