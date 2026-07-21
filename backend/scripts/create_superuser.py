#!/usr/bin/env python
"""CLI script to create a superuser for SIRMS backend.

Usage:
    python scripts/create_superuser.py
    python scripts/create_superuser.py --username admin --email admin@sirms.local
    python scripts/create_superuser.py --help
"""

import asyncio
import sys
from pathlib import Path
from getpass import getpass

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.security import User


async def create_superuser(
    username: str,
    email: str,
    full_name: str,
    password: str,
) -> User:
    """Create a superuser in the database.
    
    Args:
        username: Username for login
        email: Email address
        full_name: Full name display
        password: Plain text password (will be hashed)
        
    Returns:
        Created User instance
        
    Raises:
        ValueError: If user already exists
    """
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Check if user exists
            stmt = select(User).where(User.username == username)
            existing = await session.execute(stmt)
            if existing.scalar_one_or_none():
                raise ValueError(f"User '{username}' already exists")
            
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                password_hash=hash_password(password),
                is_locked=False,
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            return user
    finally:
        await engine.dispose()


@click.command()
@click.option("--username", prompt="Username", help="Username for login")
@click.option("--email", prompt="Email", help="Email address")
@click.option("--full-name", prompt="Full Name", help="Full name for display")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Password (will prompt if not provided)",
)
def main(username: str, email: str, full_name: str, password: str):
    """Create a new superuser for SIRMS backend."""
    try:
        user = asyncio.run(
            create_superuser(
                username=username,
                email=email,
                full_name=full_name,
                password=password,
            )
        )
        
        click.secho(
            f"✓ Superuser created successfully!",
            fg="green",
            bold=True,
        )
        click.echo(f"  Username: {user.username}")
        click.echo(f"  Email: {user.email}")
        click.echo(f"  Full Name: {user.full_name}")
        click.echo(f"  Is Locked: {user.is_locked}")
        
    except ValueError as e:
        click.secho(f"✗ Error: {str(e)}", fg="red", bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {str(e)}", fg="red", bold=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
