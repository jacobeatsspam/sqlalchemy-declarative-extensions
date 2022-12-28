from pytest_alembic import MigrationContext
from sqlalchemy import text


def test_apply_autogenerated_revision(alembic_runner: MigrationContext, alembic_engine):
    with alembic_engine.connect() as conn:
        conn.execute(text("create role write"))
        conn.execute(text("create role app"))
        conn.execute(text("commit"))

    alembic_runner.migrate_up_one()
    alembic_runner.generate_revision(autogenerate=True)
