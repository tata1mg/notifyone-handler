from enum import Enum

class Whatsapp:
    CONTENT_COLUMNS=['id','event_id','name']
    NAME =  'name'


class VariableMappingKeys(Enum):
    BODY = "body"
    HEADER = "header"
    BUTTON = "button"

class WhatsAppEventStatus(str, Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value
