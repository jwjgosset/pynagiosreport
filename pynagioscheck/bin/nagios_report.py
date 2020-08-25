"""
..  codeauthor:: Charles Blais

Check nagios and generate summary report

.. history:: Charles Blais
    Major update of the code for python3 and cleanup
"""

import logging
import argparse

from pynagioscheck import nagios
from pynagioscheck import report
from pynagioscheck import email


# Constants
DEFAULT_URL = 'http://nagios-e1.seismo.nrcan.gc.ca'
DEFAULT_KEY = '7s7jkoku'

DEFAULT_API = '/nagiosxi/api/v1/'
DEFAULT_HOSTLINK = '/nagiosxi/includes/components/xicore/status.php?host='


def main():
    """Main module (use -h for instructions)"""
    # add arguments to the parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        default=DEFAULT_URL,
        help=f'Nagios URL (default: {DEFAULT_URL}')
    parser.add_argument(
        '-k', '--key',
        default=DEFAULT_KEY,
        help=f'API key (default: {DEFAULT_KEY})')
    parser.add_argument(
        '--emails',
        nargs='+',
        help='List of emails to send too')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose')
    args = parser.parse_args()

    # turn on logging if verbose argument is specified
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.ERROR)

    api = nagios.NagiosAPI(
        f'{args.url}/{DEFAULT_API}',
        args.key)
    hosts = api.get_critical_hosts()
    services = api.get_critical_services()
    if not hosts and not services:
        logging.info('No hosts or services to report')
        return 0

    logging.info(f'Alerting on {len(hosts)} hosts \
and {len(services)} services')

    htmlreport = report.generate(
        hosts,
        services,
        link=f'{args.url}/{DEFAULT_HOSTLINK}')
    logging.info(htmlreport)

    emails = args.emails
    if not emails:
        logging.warning('No email recipients defined')
        return 0
    logging.info(f'Sending email to {"; ".join(emails)}')
    email.send(htmlreport, emails)
