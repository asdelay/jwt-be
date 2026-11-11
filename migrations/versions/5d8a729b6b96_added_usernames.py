"""added usernames

Revision ID: 5d8a729b6b96
Revises: f1e2ebc772ad
Create Date: 2026-11-11 20:48:54.607259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d8a729b6b96'
down_revision: Union[str, Sequence[str], None] = 'f1e2ebc772ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. add as nullable first: existing rows have no username yet, NOT NULL would fail immediately
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True))

    # 2. backfill: username = lowercased part of the email before '@' (cut to 40 chars to leave room for a suffix)
    op.execute("UPDATE users SET username = lower(left(split_part(email, '@', 1), 40))")

    # 3. de-duplicate: alice@a.com and alice@b.com both became 'alice'; keep the oldest (lowest id),
    #    append '_<id>' to the rest - ids are unique, so the result is unique too
    op.execute("""
        UPDATE users u
        SET username = u.username || '_' || u.id
        WHERE EXISTS (
            SELECT 1 FROM users o WHERE o.username = u.username AND o.id < u.id
        )
    """)

    # 4. now every row has a unique value -> safe to enforce the constraints
    op.alter_column('users', 'username', nullable=False)
    op.create_unique_constraint('uq_users_username', 'users', ['username'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    op.drop_column('users', 'username')
