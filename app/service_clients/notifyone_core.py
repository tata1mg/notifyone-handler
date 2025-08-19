from torpedo import CONFIG, BaseApiRequest
from torpedo.constants import HTTPMethod
from app.constants import Channels


class NotifyOneCoreClient(BaseApiRequest):
    """
    notifyone-core service client
    """

    ns_config = CONFIG.config['NOTIFYONE_CORE']
    _host = ns_config['HOST']
    _timeout = ns_config['TIMEOUT']

    @classmethod
    async def get_channel_partners_configurations(cls, channels: list[Channels]):
        """
        Use this routine to fetch the channel partners configurations.
        It returns configurations of all active channel partners of the provided channels.
        It returns default priority, custom priority and gateways for given channels
        """
        path = "/channel_partners/configurations"
        channels_str = ",".join([ch for ch in channels])
        params = {
            "channels": channels_str
        }
        result = await cls.request(
            HTTPMethod.GET.value,
            path,
            query_params=params
        )
        return result.data
