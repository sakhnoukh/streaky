"""add_not_null_constraints

Revision ID: f7g8h9i0j1k2
Revises: a1b2c3d4e5f6
Create Date: 2024-12-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'f7g8h9i0j1k2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Get the connection to check database type
    bind = op.get_bind()
    inspector = inspect(bind)
    is_sqlite = bind.dialect.name == 'sqlite'
    
    # First, update any NULL values to defaults before adding NOT NULL constraints
    # This prevents errors when altering columns
    conn = op.get_bind()
    
    # Users table: username and hashed_password should not be NULL
    # Handle NULL usernames (shouldn't exist, but handle gracefully)
    try:
        if is_sqlite:
            # SQLite uses || for concatenation
            conn.execute(sa.text("UPDATE users SET username = 'user_' || CAST(id AS TEXT) WHERE username IS NULL"))
        else:
            # For SQL Server and other databases
            # SQL Server uses + for concatenation, PostgreSQL uses ||
            if bind.dialect.name == 'mssql':
                conn.execute(sa.text("UPDATE users SET username = 'user_' + CAST(id AS VARCHAR) WHERE username IS NULL"))
            else:
                # PostgreSQL and others
                conn.execute(sa.text("UPDATE users SET username = 'user_' || CAST(id AS VARCHAR) WHERE username IS NULL"))
    except Exception:
        pass  # Table might not exist or column might already be NOT NULL
    
    # Update NULL passwords (critical - these users won't be able to log in)
    # Use a placeholder that will force password reset
    try:
        conn.execute(sa.text("UPDATE users SET hashed_password = 'MIGRATION_PLACEHOLDER' WHERE hashed_password IS NULL"))
    except Exception:
        pass
    
    # Habits table: user_id, name, goal_type should not be NULL
    try:
        # Delete orphaned habits (habits without user_id)
        conn.execute(sa.text("DELETE FROM habits WHERE user_id IS NULL"))
        # Set defaults for NULL names and goal_types
        conn.execute(sa.text("UPDATE habits SET name = 'Unnamed Habit' WHERE name IS NULL"))
        conn.execute(sa.text("UPDATE habits SET goal_type = 'daily' WHERE goal_type IS NULL"))
    except Exception:
        pass
    
    # Entries table: habit_id and date should not be NULL
    try:
        # Delete orphaned entries (entries without habit_id or date)
        conn.execute(sa.text("DELETE FROM entries WHERE habit_id IS NULL"))
        conn.execute(sa.text("DELETE FROM entries WHERE date IS NULL"))
    except Exception:
        pass
    
    # Now alter columns to be NOT NULL (only for non-SQLite databases)
    # SQLite doesn't support ALTER COLUMN, so we skip this for SQLite
    if not is_sqlite:
        try:
            # Users table
            op.alter_column('users', 'username',
                           existing_type=sa.String(255),
                           nullable=False)
        except Exception:
            pass  # Column might already be NOT NULL
        
        try:
            op.alter_column('users', 'hashed_password',
                           existing_type=sa.String(255),
                           nullable=False)
        except Exception:
            pass
        
        # Habits table
        try:
            op.alter_column('habits', 'user_id',
                           existing_type=sa.INTEGER(),
                           nullable=False)
        except Exception:
            pass
        
        try:
            op.alter_column('habits', 'name',
                           existing_type=sa.String(255),
                           nullable=False)
        except Exception:
            pass
        
        try:
            op.alter_column('habits', 'goal_type',
                           existing_type=sa.String(50),
                           nullable=False)
        except Exception:
            pass
        
        # Entries table
        try:
            op.alter_column('entries', 'habit_id',
                           existing_type=sa.INTEGER(),
                           nullable=False)
        except Exception:
            pass
        
        try:
            op.alter_column('entries', 'date',
                           existing_type=sa.DATE(),
                           nullable=False)
        except Exception:
            pass
    # For SQLite, the constraints are enforced at the application level
    # SQLite doesn't support ALTER COLUMN, but the application will enforce NOT NULL


def downgrade():
    # Get the connection to check database type
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == 'sqlite'
    
    # Revert columns back to nullable (only for non-SQLite databases)
    if not is_sqlite:
        # Entries table
        op.alter_column('entries', 'date',
                       existing_type=sa.DATE(),
                       nullable=True)
        op.alter_column('entries', 'habit_id',
                       existing_type=sa.INTEGER(),
                       nullable=True)
        
        # Habits table
        op.alter_column('habits', 'goal_type',
                       existing_type=sa.String(50),
                       nullable=True)
        op.alter_column('habits', 'name',
                       existing_type=sa.String(255),
                       nullable=True)
        op.alter_column('habits', 'user_id',
                       existing_type=sa.INTEGER(),
                       nullable=True)
        
        # Users table
        op.alter_column('users', 'hashed_password',
                       existing_type=sa.String(255),
                       nullable=True)
        op.alter_column('users', 'username',
                       existing_type=sa.String(255),
                       nullable=True)
