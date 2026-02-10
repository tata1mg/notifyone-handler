import logging

import firebase_admin
from firebase_admin import credentials

from .config_provider import ConfigProvider

logger = logging.getLogger(__name__)


class CredentialProvider:
    def __init__(self, config_provider: ConfigProvider):
        self._config_provider = config_provider
        self._initialize_firebase_admin()

    def _initialize_firebase_admin(self):
        try:
            cred = credentials.Certificate(self._config_provider.service_account_info)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.error("Failed to initialize Firebase Admin: %s", e)
            raise

    @property
    def credentials(self):
        return firebase_admin.get_app().credential
