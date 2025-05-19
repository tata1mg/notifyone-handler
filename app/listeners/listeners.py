import asyncio
from torpedo.constants import ListenerEventTypes
from asyncpg import CharacterNotInRepertoireError

from app.initialize import Initialize
from app.services.channel_partners.get_configurations import ChannelPartners


async def initialize_sqs_subscribers(app, loop):
    await Initialize.initialize_sqs_subscribers()


async def channel_partners_configurations(app, loop):
    asyncio.create_task(ChannelPartners.refresh_cp_configurations())


async def setup_channel_partners_configurations_periodic_refresh(app, loop):
    # Fetch channel partners configurations periodically
    asyncio.create_task(ChannelPartners.fetch_channel_partners_configurations_periodically())


listeners = [
    (initialize_sqs_subscribers, ListenerEventTypes.AFTER_SERVER_START.value),
    (channel_partners_configurations, ListenerEventTypes.AFTER_SERVER_START.value),
    (setup_channel_partners_configurations_periodic_refresh, ListenerEventTypes.AFTER_SERVER_START.value)
]
