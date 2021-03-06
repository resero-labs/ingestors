from __future__ import unicode_literals

import logging
from olefile import isOleFile
from email.parser import Parser

from ingestors.base import Ingestor
from ingestors.support.email import EmailSupport
from ingestors.support.ole import OLESupport
from ingestors.email.outlookmsg_lib import Message
from ingestors.util import safe_string, safe_dict

log = logging.getLogger(__name__)


class OutlookMsgIngestor(Ingestor, EmailSupport, OLESupport):
    MIME_TYPES = [
        'appliation/msg',
        'appliation/x-msg',
        'message/rfc822'
    ]
    EXTENSIONS = [
        'msg'
    ]
    SCORE = 10

    def _parse_headers(self, message):
        headers = message.getField('007D')
        if headers is not None:
            try:
                message = Parser().parsestr(headers, headersonly=True)
                self.extract_headers_metadata(message.items())
                return
            except Exception:
                log.warning("Cannot parse headers: %s" % headers)

        self.result.headers = safe_dict({
            'Subject': message.getField('0037'),
            'BCC': message.getField('0E02'),
            'CC': message.getField('0E03'),
            'To': message.getField('0E04'),
            'From': message.getField('1046'),
            'Message-ID': message.getField('1035'),
        })

    def ingest(self, file_path):
        message = Message(file_path)
        self._parse_headers(message)
        self.extract_plain_text_content(message.getField('1000'))
        self.update('message_id', message.getField('1035'))

        # all associated person names, i.e. sender, recipient etc.
        NAME_FIELDS = ['0C1A', '0E04', '0040', '004D']
        EMAIL_FIELDS = ['0C1F', '0076', '0078', '1046', '3003',
                        '0065', '3FFC', '403E']
        for field in NAME_FIELDS + EMAIL_FIELDS:
            self.parse_emails(message.getField(field))

        self.update('title', message.getField('0037'))
        self.update('title', message.getField('0070'))
        self.update('author', message.getField('0C1A'))

        # from pprint import pprint
        # pprint(self.result.to_dict())

        self.extract_olefileio_metadata(message)
        self.result.flag(self.result.FLAG_EMAIL)
        self.result.flag(self.result.FLAG_PLAINTEXT)
        for attachment in message.attachments:
            name = safe_string(attachment.longFilename)
            name = name or safe_string(attachment.shortFilename)
            self.ingest_attachment(name,
                                   attachment.mimeType,
                                   attachment.data)

    @classmethod
    def match(cls, file_path, result=None):
        if isOleFile(file_path):
            return super(OutlookMsgIngestor, cls).match(file_path,
                                                        result=result)
        return -1
