import jwt
import time
import asyncio

import logging

logger = logging.getLogger()


class CredentialProvider:
    _token = None
    _config = None
    _refresh_token_task = None

    @classmethod
    async def init(cls, config):
        cls._config = config
        print("Initializing CredentialProvider for APNs")
        await cls.start_refresh_token_task()

    @classmethod
    def _get_new_token(cls, algorithm, secret, team_id, key_id):
        token = jwt.encode(
            {"iss": team_id, "iat": time.time()},
            secret,
            algorithm=algorithm,
            headers={
                "alg": algorithm,
                "kid": key_id,
            },
        )

        return token

    @classmethod
    async def _refresh_token(cls):
        print("Starting token refresh task")
        delay = cls._config.get("REFRESH_TOKEN_DELAY")  # in seconds

        alg = cls._config.get("ALGORITHM")
        team_id = cls._config.get("TEAM_ID")
        key_id = cls._config.get("KEY_ID")
        secret = cls._config.get("PRIVATE_KEY")
        print("Starting token refresh task with delay:", delay, "algorithm:", alg)
        while True:
            try:
                token = cls._get_new_token(alg, secret, team_id, key_id)
                cls._token = token
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                logger.info("Refresh Token task cancelled")
            except Exception as err:
                logger.exception("Encountered error while refreshing token %s", err)
                return

    @classmethod
    async def start_refresh_token_task(cls):
        # start refreshing token when service starts up
        task = asyncio.create_task(cls._refresh_token())
        cls._refresh_token_task = task

    @classmethod
    def cancel_refresh_token_task(cls):
        # cancel refreshing token when shutting server down
        if cls._refresh_token_task:
            cls._refresh_token_task.cancel()

    @property
    def token(self):
        return self._token
