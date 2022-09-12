"""
..  codeauthor:: Charles Blais

Check nagios and generate summary report

.. history:: Charles Blais
    Major update of the code for python3 and cleanup
"""
import logging

from typing import List, Optional, Union

import click

from pynagiosreport.config import get_app_settings, LogLevels

from pynagiosreport.nagios.api import NagiosAPI

from pynagiosreport.nagios.statusfile import StatusFile

from pynagiosreport.email import send as send_email

from pynagiosreport.rave import send as send_rave, get_description

from pynagiosreport.models import \
    HostStatus, HostStatusCore, ServiceStatus, ServiceStatusCore


settings = get_app_settings()


@click.command()
@click.option(
    '--url',
    default=settings.url,
    help='Nagios URL'
)
@click.option(
    '--apikey',
    help='Nagios XI API user token'
)
@click.option(
    '--status-file',
    default=settings.status_file,
    help='status.dat file alternative to url if no apikey defined'
)
@click.option(
    '-e', '--emails',
    multiple=True,
    help='Email address to send to'
)
@click.option(
    '--allow-empty-email',
    is_flag=True,
    help='Allow sending empty email (0 count email)'
)
@click.option(
    '--stdout',
    is_flag=True,
    help='Send report by stdout'
)
@click.option(
    '--log-level',
    type=click.Choice([v.value for v in LogLevels]),
    help='Verbosity'
)
def main(
    url: str,
    apikey: Optional[str],
    status_file: str,
    emails: List[str],
    allow_empty_email: bool,
    stdout: bool,
    log_level: str,
):
    """
    Get all critical hosts/services that the API token can see and send
    a report to all those in recipients.

    Some variables can be configured using envrionment variables; such as
    Rave destination.  For the complete list, look at config.py.
    """
    settings.url = url
    if apikey is not None:
        settings.apikey = apikey
    if status_file is not None:
        settings.status_file = status_file
    if log_level is not None:
        settings.log_level = LogLevels[log_level]
    settings.configure_logging()

    # defined the type of the hosts/services structure for typing
    hosts: Union[List[HostStatus], List[HostStatusCore]]
    services: Union[List[ServiceStatus], List[ServiceStatusCore]]

    # Create api client if the API key is set and get
    # the failed services/hosts, if not, use the status.dat
    if settings.apikey:
        api = NagiosAPI(settings.url_api, settings.apikey)
        hosts = api.get_critical_hosts()
        services = api.get_critical_services()
    else:
        stat = StatusFile(settings.status_file)
        hosts = stat.get_critical_hosts()
        services = stat.get_critical_services()

    total_critical = len(hosts) + len(services)

    # No send the reports based on the set parameters
    if len(emails):
        logging.info(f'Preparing emailing to {emails}')
        if not allow_empty_email and total_critical == 0:
            logging.info('Empty email, do not send')
        else:
            logging.info('Sending email')
            send_email(hosts, services, emails)

    if (
        settings.rave_url and
        settings.rave_username and
        settings.rave_password
    ):
        logging.info('Preparing sending by rave')
        send_rave(hosts, services)

    if stdout:
        print(get_description(hosts, services))
