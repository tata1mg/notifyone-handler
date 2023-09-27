class Response:
    def __init__(self, response: dict):
        if not (response and response.get("Messages")):
            self.messages = []
        else:
            self.messages = [Message(message) for message in response["Messages"]]


class Message:
    def __init__(self, message: dict):
        if not message:
            self.body = None
            self.attributes = []
            self.receipt_handle = None
        else:
            self.body = message["Body"]
            message_attributes = message.get("MessageAttributes", {})
            self.attributes = [
                Attribute(attribute_name, message_attributes[attribute_name])
                for attribute_name in message_attributes
            ]
            self.receipt_handle = message["ReceiptHandle"]


class Attribute:
    def __init__(self, attribute_name: str, attribute_data: dict):
        self.name = attribute_name
        self.value = attribute_data.get("StringValue")
