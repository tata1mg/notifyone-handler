from torpedo.constants import ListenerEventTypes

from app.initialize import Initialize


async def initialize_sqs_subscribers(app, loop):
    await Initialize.initialize_sqs_subscribers()


listeners = [
    (initialize_sqs_subscribers, ListenerEventTypes.AFTER_SERVER_START.value),
]
