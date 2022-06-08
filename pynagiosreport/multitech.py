"""
..  codeauthor:: Charles Blais <charles.blais@canada.ca>

:mod:`pychismsg.multitech` -- MultiTech API
=======================================
"""
import base64

import logging

# Third-party library
import requests

# User-contributed library
from .models import MultitechSender, MultitechRecipient

from .config import get_app_settings


class MultitechFax:
    '''
    Multitech Fax setting and configuration
    '''
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 80,
        url: str = '/ffws/v1/ofax',
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.url = url

    def _send_to_host(
        self,
        sender: MultitechSender,
        recipient: MultitechRecipient,
        content: str,
    ):
        settings = get_app_settings()
        data = settings.j2_fax_template.render(
            sender=sender,
            recipient=recipient,
            b64content=base64.b64encode(content.encode()).decode('utf-8')
        )

        url = f'http://{self.host}:{self.port}{self.url}'
        logging.info(f'Sending fax to {url}')
        # Post the message
        req = requests.post(
            url,
            data=data,
            auth=requests.auth.HTTPBasicAuth(
                self.username,
                self.password))
        # raise an error if it didn't work
        req.raise_for_status()

    def send(
        self,
        sender: MultitechSender,
        recipient: MultitechRecipient,
        content: str = 'empty',
    ):
        """
        Send from sender to recipient the content

        :type sender: :class:`pychismsg.call.Sender`
        :param sender: sender information
        :type recipient: :class:`pychismsg.Recipient`
        :param recipient: recipient information
        :param str content: content to send
        """
        self._send_to_host(
            sender,
            recipient,
            content
        )
