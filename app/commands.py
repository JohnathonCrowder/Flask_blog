import click
from flask.cli import with_appcontext
from .models import db, User
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(username, email, password):
    logger.info(f"Attempting to create admin user: {username}")
    try:
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                logger.info(f"IntegrityError caught: UNIQUE constraint failed: user.username")
                raise ValueError(f"Username '{username}' already exists.")
            else:
                logger.info(f"IntegrityError caught: UNIQUE constraint failed: user.email")
                raise ValueError(f"Email '{email}' already exists.")
        
        user = User(username=username, email=email, is_admin=True)
        logger.info("User object created")
        user.set_password(password)
        logger.info("Password set")
        db.session.add(user)
        logger.info("User added to session")
        db.session.commit()
        logger.info("Session committed")
        click.echo(f"Admin user {username} created successfully.")
    except ValueError as e:
        db.session.rollback()
        click.echo(str(e))
    except Exception as e:
        logger.info(f"Unexpected error: {str(e)}")
        db.session.rollback()
        click.echo(f"An error occurred: {str(e)}")

def init_app(app):
    logger.info("Initializing admin command")
    app.cli.add_command(create_admin)