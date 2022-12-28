import pytest
import sqlalchemy.exc
from pytest_alembic import MigrationContext, tests
from pytest_mock_resources import PostgresConfig, create_postgres_fixture
from sqlalchemy import text

alembic_engine = create_postgres_fixture(scope="function", engine_kwargs={"echo": True})


@pytest.fixture(scope="session")
def pmr_postgres_config():
    return PostgresConfig(port=None, ci_port=None)


def test_apply_autogenerated_revision(alembic_runner: MigrationContext, alembic_engine):
    alembic_runner.generate_revision(autogenerate=True, prevent_file_generation=False)
    alembic_runner.migrate_up_one()

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        with alembic_engine.connect() as conn:
            conn.execute(text("REFRESH MATERIALIZED VIEW bar"))

    with alembic_engine.connect() as conn:
        conn.execute(text("REFRESH MATERIALIZED VIEW baz"))

        result = list(conn.execute(text("select num, num2 from baz")).fetchall())

    expected_result = [(1, 1), (2, 1)]
    assert expected_result == result

    # Verify this no longer sees changes to make! Failing here would imply the autogenerate
    # is not fully normalizing the difference.
    tests.test_model_definitions_match_ddl(alembic_runner)
