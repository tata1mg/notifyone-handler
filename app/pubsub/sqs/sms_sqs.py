from commonutils import BaseSQSWrapper


class APIClientSQS(BaseSQSWrapper):
    sqs_handler = None

    def __init__(self, config: dict = {}) -> None:
        self.config = config or {"SQS": {}}
        super().__init__(self.config)
