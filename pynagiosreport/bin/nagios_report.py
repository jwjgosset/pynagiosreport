"""
..  codeauthor:: Charles Blais

Check nagios and generate summary report

.. history:: Charles Blais
    Major update of the code for python3 and cleanup
"""
import logging

from typing import List

import click

from pynagiosreport.config import get_app_settings, LogLevels

from pynagiosreport.nagios import NagiosAPI

from pynagiosreport.email import send


settings = get_app_settings()


@click.command()
@click.option(
    '--url',
    default=settings.url,
    help='Nagios URL'
)
@click.option(
    '--apikey',
    default=settings.apikey,
    help='Nagios XI API user token'
)
@click.option(
    '-e', '--emails',
    required=True,
    multiple=True,
    help='Email address to send to'
)
@click.option(
    '--allow-empty-email',
    is_flag=True,
    help='Allow sending empty email (non-critical'
)
@click.option(
    '--log-level',
    type=click.Choice([v.value for v in LogLevels]),
    help='Verbosity'
)
def main(
    url: str,
    apikey: str,
    emails: List[str],
    allow_empty_email: bool,
    log_level: str,
):
    """
    Get all critical hosts/services that the API token can see and send
    a report to all those in recipients.
    """
    settings.url = url
    settings.apikey = apikey
    if log_level is not None:
        settings.log_level = LogLevels[log_level]
    settings.configure_logging()

    # Create api client
    api = NagiosAPI(settings.url_api, settings.apikey)
    hosts = api.get_critical_hosts()
    services = api.get_critical_services()

    if not allow_empty_email and (len(hosts) == 0 or len(services) == 0):
        logging.info('Empty email, do not send')
        return

    send(
        hosts=hosts,
        services=services,
        recipients=emails,
    )
