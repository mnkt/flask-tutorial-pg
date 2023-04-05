import psycopg2
import psycopg2.extras
import click
from flask import current_app
from flask import g


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            current_app.config['DATABASE'],
            cursor_factory=psycopg2.extras.DictCursor
        )

    return g.db

def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:

        if e is None:
            db.commit()
        else:
            db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        sql_commands = f.read().decode("utf8").split(";")
        for command in sql_commands:
            if command.strip():
                db.cursor().execute(command)
    db.commit()


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
