import click
from flask import Flask
from flask.cli import with_appcontext

from seeds.client_seed import seed_dev_client
from seeds.user_seed import DEV_USER_EMAIL, DEV_USER_PASSWORD, seed_dev_user


@click.command("seed")
@with_appcontext
def seed_command():
    """Load development seed data."""
    client = seed_dev_client()
    click.echo(f"Seeded client: {client.name} ({client.id})")

    user = seed_dev_user()
    click.echo(f"Seeded user: {user.email} ({user.id})")
    click.echo(f"Dev login: {DEV_USER_EMAIL} / {DEV_USER_PASSWORD}")


def register_seed_commands(app: Flask) -> None:
    app.cli.add_command(seed_command)
