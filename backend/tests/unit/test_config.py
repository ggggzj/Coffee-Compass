from app.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "g")
    monkeypatch.setenv("OPENAI_API_KEY", "o")
    s = Settings()
    assert s.database_url == "postgresql+asyncpg://test:test@localhost/test"
    assert s.embedding_model == "text-embedding-3-small"
    assert s.usc_lat == 34.0224
