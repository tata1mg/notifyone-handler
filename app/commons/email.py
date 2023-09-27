from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Recipients:
    to: List[str]
    cc: List[str]
    bcc: List[str]

    def _convert_to_list(self, emails: Union[str, List[str]]) -> List[str]:
        if not emails:
            return []

        if isinstance(emails, list):
            return emails
        return emails.split(",")

    def __init__(self, to: str, cc: str, bcc: str) -> None:
        self.to = self._convert_to_list(to)
        self.cc = self._convert_to_list(cc)
        self.bcc = self._convert_to_list(bcc)


@dataclass
class Message:
    subject: str
    html_body: Optional[str]
    text_body: Optional[str] = None
    files: Optional[List[str]] = None
