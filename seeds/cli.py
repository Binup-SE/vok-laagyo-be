import click
from flask import Flask
from flask.cli import with_appcontext


@click.command("seed")
@with_appcontext
def seed_command():
    """Load development seed data (tenants, users, memberships)."""
    from seeds import tenants, users

    tenant_created = tenants.run()
    user_created = users.run()

    if tenant_created:
        click.echo(f"Seeded tenants: {', '.join(tenant_created)}")
    if user_created:
        click.echo(f"Seeded users: {', '.join(user_created)}")
    if not tenant_created and not user_created:
        click.echo("Seeds already present — nothing to do.")


def register_seed_commands(app: Flask) -> None:
    app.cli.add_command(seed_command)
