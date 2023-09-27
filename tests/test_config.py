import pytest
from torpedo import Host
from torpedo.common_utils import CONFIG, json_file_to_dict

config = CONFIG.config
config_template = json_file_to_dict("./config_template.json")


@pytest.yield_fixture(scope="session")
def app():
    Host._name = config["NAME"]
    _app = Host.get_app()
    _app.update_config(config)
    yield _app


def test_load_from_file(app):
    assert "NAME" in app.config
    assert app.config.NAME == "service-name"
    assert "HOST" in app.config
    assert app.config.HOST == "0.0.0.0"
    assert "POSTGRES_HOST" in app.config
    assert app.config.POSTGRES_HOST not in (None, "")


def test_config_template_sync_with_config_file(app):
    template_keys = set(config_template.keys())
    config_keys = set(config.keys())
    assert (config_keys - template_keys) == set()
