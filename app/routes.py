from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html', company_name="{COMPANY_NAME}")

@main.route('/about')
def about():
    return render_template('about.html', company_name="{COMPANY_NAME}")

@main.route('/contact')
def contact():
    return render_template('contact.html', company_name="{COMPANY_NAME}")