import unittest

from app.database.deps import resolve_database_url


class DatabaseConfigurationTests(unittest.TestCase):
    def test_local_development_defaults_to_sqlite(self):
        self.assertEqual(
            resolve_database_url("development", None),
            "sqlite:///./clearpte_local.db",
        )

    def test_production_requires_explicit_database_url(self):
        for environment in ("production", "prod", "staging", "stage"):
            with self.subTest(environment=environment):
                with self.assertRaisesRegex(RuntimeError, "DATABASE_URL must be configured"):
                    resolve_database_url(environment, None)

    def test_production_rejects_sqlite(self):
        with self.assertRaisesRegex(RuntimeError, "SQLite is not supported"):
            resolve_database_url("production", "sqlite:///./local.db")

    def test_production_accepts_configured_postgresql(self):
        database_url = "postgresql+psycopg2://user:password@db.example.test/app"
        self.assertEqual(resolve_database_url("production", database_url), database_url)

    def test_unrecognized_environment_is_normalized_and_uses_local_default(self):
        self.assertEqual(
            resolve_database_url("development", " sqlite:///tmp/test.sqlite "),
            "sqlite:///tmp/test.sqlite",
        )


if __name__ == "__main__":
    unittest.main()
