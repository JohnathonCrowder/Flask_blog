from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user
from .models import db, Post, User
from sqlalchemy import func, or_

main = Blueprint('main', __name__)



@main.route('/')
def home():
    # Featured section
    featured_posts = Post.query.filter_by(status='published').order_by(Post.created_at.desc()).limit(3).all()
    
    # Recent posts section
    recent_posts = Post.query.filter_by(status='published').order_by(Post.created_at.desc()).limit(6).all()
    
    # Featured authors (could be based on post count or other criteria)
    featured_authors = User.query.join(Post).group_by(User.id).order_by(func.count(Post.id).desc()).limit(3).all()
    
    return render_template('index.html', 
                          company_name="{COMPANY_NAME}",
                          featured_posts=featured_posts,
                          recent_posts=recent_posts,
                          featured_authors=featured_authors)

@main.route('/about')
def about():
    # Get some statistics for the about page
    total_posts = Post.query.count()
    total_authors = User.query.count()
    
    return render_template('about.html', 
                          company_name="{COMPANY_NAME}",
                          total_posts=total_posts,
                          total_authors=total_authors)

@main.route('/contact')
def contact():
    return render_template('contact.html', company_name="{COMPANY_NAME}")



@main.route('/dashboard')
@login_required
def user_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    featured_posts = Post.query.filter_by(status='published').order_by(Post.created_at.desc()).limit(3).all()
    recent_posts = Post.query.filter_by(status='published').order_by(Post.created_at.desc()).limit(5).all()
    return render_template('user/user_dashboard.html', 
                         featured_posts=featured_posts, 
                         recent_posts=recent_posts)

@main.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    # Here you would add logic to handle the subscription
    # This might involve adding the email to a mailing list service
    # or storing it in your database
    flash('Thank you for subscribing!', 'success')
    return redirect(url_for('main.user_dashboard'))

@main.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        search_results = Post.query.filter(
            db.or_(
                Post.title.ilike(f'%{query}%'),
                Post.content.ilike(f'%{query}%'),
                Post.tags.ilike(f'%{query}%')
            )
        ).filter_by(status='published').order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    else:
        search_results = None
    
    return render_template('search.html', 
                         query=query,
                         results=search_results)


@main.route('/manage-account', methods=['GET', 'POST'])
@login_required
def manage_account():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'error')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Your password has been updated successfully.', 'success')
                return redirect(url_for('main.manage_account'))
        
        elif action == 'delete_account':
            password = request.form.get('delete_password')
            if current_user.check_password(password):
                db.session.delete(current_user)
                db.session.commit()
                logout_user()
                flash('Your account has been deleted successfully.', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Incorrect password. Account not deleted.', 'error')
    
    return render_template('user/manage_account.html')

# Error handlers
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', company_name="{COMPANY_NAME}"), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', company_name="{COMPANY_NAME}"), 500