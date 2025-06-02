import asyncio
from torpedo.constants import ListenerEventTypes
from asyncio import Queue
from app.initialize import Initialize
from app.services.channel_partners.get_configurations import ChannelPartners
from app.services.handlers.push.apns.credential_provider import CredentialProvider


# Add this new function
async def setup_logger_queue(app, loop):
    """Initialize logger queue for sanic-ext compatibility"""
    if not hasattr(app.shared_ctx, "logger_queue"):
        app.shared_ctx.logger_queue = Queue()

async def initilialize_startup_tasks(_app, _loop):
    await Initialize.initialize_startup_tasks()

async def stop_apns_refresh_tokens(_app, _loop):
    await CredentialProvider.cancel_refresh_token_task()

def initialize_service_startup_dependencies(app, loop):
    """
    Initialize service startup dependencies.
    This function is called before the server starts.
    """
    # Initialize service startup dependencies
    Initialize.initialize_service_startup_dependencies()

async def initialize_sqs_subscribers(app, loop):
    await Initialize.initialize_sqs_subscribers()


async def channel_partners_configurations(app, loop):
    asyncio.create_task(ChannelPartners.refresh_cp_configurations())


async def setup_channel_partners_configurations_periodic_refresh(app, loop):
    # Fetch channel partners configurations periodically
    asyncio.create_task(ChannelPartners.fetch_channel_partners_configurations_periodically())


listeners = [
    (setup_logger_queue, ListenerEventTypes.BEFORE_SERVER_START.value), 
    (initialize_sqs_subscribers, ListenerEventTypes.AFTER_SERVER_START.value),
    (initialize_service_startup_dependencies, ListenerEventTypes.BEFORE_SERVER_START.value),
    (initilialize_startup_tasks, ListenerEventTypes.AFTER_SERVER_START.value),
    (stop_apns_refresh_tokens, ListenerEventTypes.AFTER_SERVER_STOP.value),
    (channel_partners_configurations, ListenerEventTypes.AFTER_SERVER_START.value),
    (setup_channel_partners_configurations_periodic_refresh, ListenerEventTypes.AFTER_SERVER_START.value)
]
