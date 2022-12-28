import pytest
from pytest_alembic import MigrationContext
from pytest_mock_resources import PostgresConfig, create_postgres_fixture
from sqlalchemy import text

alembic_engine = create_postgres_fixture(scope="function", engine_kwargs={"echo": True})


@pytest.fixture(scope="session")
def pmr_postgres_config():
    return PostgresConfig(port=None, ci_port=None)


def test_apply_autogenerated_revision(alembic_runner: MigrationContext, alembic_engine):
    result = alembic_runner.generate_revision(
        autogenerate=True, prevent_file_generation=False
    )
    alembic_runner.migrate_up_one()

    with alembic_engine.connect() as conn:
        result = [r for r, in conn.execute(text("select * from bar")).fetchall()]

    expected_result = [11, 12]
    assert expected_result == result
