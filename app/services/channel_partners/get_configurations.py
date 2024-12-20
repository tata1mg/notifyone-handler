import asyncio
import logging

from app.constants import Channels
from app.services.handlers.email.handler import EmailHandler
from app.services.handlers.sms.handler import SmsHandler
from app.services.handlers.push.handler import PushHandler
from app.services.handlers.whatsapp.handler import WhatsappHandler
from app.service_clients.notifyone_core import NotifyOneCoreClient

logger = logging.getLogger()


class ChannelPartners:

    _periodic_sync_delay = 5*60
    PROVIDERS_CONFIG = dict()

    @classmethod
    async def fetch_channel_partners_configurations_periodically(cls):
        # sleep for cls._sync_delay seconds
        await asyncio.shield(asyncio.sleep(cls._periodic_sync_delay))
        logger.info('Fetching CPs configurations after {} seconds'.format(cls._periodic_sync_delay))
        try:
            # refresh configuration
            await cls.refresh_cp_configurations()
        except Exception as e:
            pass
            # logger.error('refresh_app_events_periodically failed with error - {}'.format(str(e)))
        finally:
            # recursive call
            asyncio.create_task(cls.fetch_channel_partners_configurations_periodically())

    @classmethod
    async def refresh_cp_configurations(cls):
        configurations = await cls.get_channel_partners_configurations(Channels.get_all_values())

        email_configuration = configurations[Channels.EMAIL.value]
        sms_configuration = configurations[Channels.SMS.value]
        push_configuration = configurations[Channels.PUSH.value]
        whatsapp_configuration = configurations[Channels.WHATSAPP.value]

        EmailHandler.update_configuration(email_configuration)
        SmsHandler.update_configuration(sms_configuration)
        PushHandler.update_configuration(push_configuration)
        WhatsappHandler.update_configuration(whatsapp_configuration)

    @classmethod
    async def get_channel_partners_configurations(cls, channels: list[Channels]):
        configuration_data = await NotifyOneCoreClient.get_channel_partners_configurations(channels)
        return configuration_data
