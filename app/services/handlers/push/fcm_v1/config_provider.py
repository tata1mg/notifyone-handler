from typing import Dict


class ConfigProvider:
    def __init__(self, config: Dict):
        self._config = config

    @property
    def project_id(self) -> str:
        return self._config.get("PROJECT_ID", "")

    @property
    def service_account_info(self) -> Dict:
        return {
            "type": self._config.get("TYPE"),
            "project_id": self.project_id,
            "private_key_id": self._config.get("PRIVATE_KEY_ID"),
            "private_key": self._config.get("PRIVATE_KEY"),
            "client_email": self._config.get("CLIENT_EMAIL"),
            "client_id": self._config.get("CLIENT_ID"),
            "token_uri": self._config.get("TOKEN_URI"),
            "auth_uri": self._config.get("AUTH_URI"),
            "auth_provider_x509_cert_url": self._config.get(
                "AUTH_PROVIDER_X509_CERT_URL"
            ),
            "client_x509_cert_url": self._config.get("CLIENT_X509_CERT_URL"),
            "universe_domain": self._config.get("UNIVERSE_DOMAIN"),
        }
