import click
from flask.cli import with_appcontext
from .models import db, User

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(username, email, password):
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Admin user {username} created successfully.")

def init_app(app):
    app.cli.add_command(create_admin)