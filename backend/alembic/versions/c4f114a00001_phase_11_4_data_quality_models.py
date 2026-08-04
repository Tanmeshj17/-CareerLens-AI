"""Phase 11.4 Data Quality Models

Revision ID: c4f114a00001
Revises: 8ed26c9152c4
Create Date: 2026-07-31 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4f114a00001'
down_revision: Union[str, None] = '8ed26c9152c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. pipeline_run_metrics
    op.create_table(
        'pipeline_run_metrics',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('pipeline_name', sa.String(), nullable=True, index=True),
        sa.Column('run_id', sa.String(), nullable=True, index=True),
        sa.Column('started_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('collectors_run', sa.Integer(), nullable=True, default=0),
        sa.Column('collectors_ok', sa.Integer(), nullable=True, default=0),
        sa.Column('collectors_failed', sa.Integer(), nullable=True, default=0),
        sa.Column('collectors_zero_result', sa.Integer(), nullable=True, default=0),
        sa.Column('collectors_slow', sa.Integer(), nullable=True, default=0),
        sa.Column('total_collected', sa.Integer(), nullable=True, default=0),
        sa.Column('total_inserted', sa.Integer(), nullable=True, default=0),
        sa.Column('total_updated', sa.Integer(), nullable=True, default=0),
        sa.Column('total_duplicates', sa.Integer(), nullable=True, default=0),
        sa.Column('total_errors', sa.Integer(), nullable=True, default=0),
        sa.Column('total_broken_links', sa.Integer(), nullable=True, default=0),
        sa.Column('rows_per_second', sa.Float(), nullable=True),
        sa.Column('insert_speed_ms', sa.Float(), nullable=True),
        sa.Column('update_speed_ms', sa.Float(), nullable=True),
        sa.Column('peak_memory_mb', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, default="RUNNING"),
        sa.Column('error_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # 2. company_aliases
    op.create_table(
        'company_aliases',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('alias', sa.String(), nullable=True, unique=True, index=True),
        sa.Column('canonical_name', sa.String(), nullable=True, index=True),
        sa.Column('source', sa.String(), nullable=True, default="HARDCODED"),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # 3. location_norms
    op.create_table(
        'location_norms',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('raw_location', sa.String(), nullable=True, unique=True, index=True),
        sa.Column('city', sa.String(), nullable=True, index=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True, default="India"),
        sa.Column('is_remote', sa.Boolean(), nullable=True, default=False),
        sa.Column('source', sa.String(), nullable=True, default="HARDCODED"),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # 4. data_alerts
    op.create_table(
        'data_alerts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('alert_type', sa.String(), nullable=True, index=True),
        sa.Column('severity', sa.String(), nullable=True, index=True, default="WARNING"),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('metric_name', sa.String(), nullable=True),
        sa.Column('metric_value', sa.Float(), nullable=True),
        sa.Column('threshold', sa.Float(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=True, default=False, index=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('cooldown_key', sa.String(), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, index=True),
    )


def downgrade() -> None:
    op.drop_table('data_alerts')
    op.drop_table('location_norms')
    op.drop_table('company_aliases')
    op.drop_table('pipeline_run_metrics')
