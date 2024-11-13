from flask import Flask, render_template, url_for

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template('index.html', company_name="{COMPANY_NAME}")

    @app.route('/about')
    def about():
        return render_template('about.html', company_name="{COMPANY_NAME}")

    @app.route('/contact')
    def contact():
        return render_template('contact.html', company_name="{COMPANY_NAME}")

    return app
