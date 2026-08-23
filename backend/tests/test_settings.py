from pathlib import Path

from app.config.settings import Settings, _BACKEND_ROOT


def test_cors_origins_default_is_parsed_to_a_list() -> None:
    settings = Settings(ai_api_key="")
    assert settings.cors_allow_origins_list == ["http://localhost:5173"]


def test_cors_origins_splits_comma_separated_value() -> None:
    settings = Settings(ai_api_key="", cors_allow_origins="http://a.com, http://b.com")
    assert settings.cors_allow_origins_list == ["http://a.com", "http://b.com"]


def test_settings_load_cleanly_from_a_dotenv_style_value(tmp_path, monkeypatch) -> None:
    # Regression test: pydantic-settings tries to JSON-decode env values for
    # list-typed fields before any validator runs, which used to blow up
    # SettingsError for a plain "a,b" .env value. cors_allow_origins must
    # stay a plain str field (see settings.py) so this keeps working.
    env_file = tmp_path / ".env"
    env_file.write_text("CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000\n")

    settings = Settings(ai_api_key="", _env_file=str(env_file))
    assert settings.cors_allow_origins_list == [
        "http://localhost:5173",
        "http://localhost:3000",
    ]


def test_default_env_file_is_absolute_and_independent_of_process_cwd() -> None:
    # Regression test: this used to be the bare string ".env", which
    # pydantic-settings resolves against the process's current working
    # directory - not this module's location. uvicorn is launched from the
    # repo root here (see .claude/launch.json's `--app-dir backend`), so a
    # relative path silently missed backend/.env and fell back to defaults
    # with no error at all (AI_API_KEY, TESSERACT_CMD, etc. all went blank).
    env_file = Path(Settings.model_config["env_file"])
    assert env_file.is_absolute()
    assert env_file == _BACKEND_ROOT / ".env"
    assert _BACKEND_ROOT.name == "backend"
