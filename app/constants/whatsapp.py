from enum import Enum

class Whatsapp:
    CONTENT_COLUMNS=['id','event_id','name']
    NAME =  'name'


class VariableMappingKeys(Enum):
    BODY = "body"
    HEADER = "header"
    BUTTON = "button"
