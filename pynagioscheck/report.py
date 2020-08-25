"""
..  codeauthor:: Charles Blais
"""
from typing import List


def _get_html_hosts_report(
    hosts: List,
    link: str = ''
) -> str:
    """
    Generate the Hosts HTML report.  We assume duplicate records to be
    removed at this stage.

    :return: string html report
    """
    hosts = sorted(
        hosts,
        key=lambda host: host.get('status_update_time'),
        reverse=True)

    html_hosts = ''
    for host in hosts:
        if link:
            name = '<a href="{link}{host}">{host}</a>'.format(
                link=link,
                host=host.get('host_name')
            )
        else:
            name = host.get('host_name')

        html_hosts += f'''
            <tr>
                <td>{name}</td>
                <td>{host.get('output')}</td>
                <td>{host.get('status_update_time')}</td>
                <td>{host.get('last_time_up')}</td>
            </tr>'''

    return f'''
        <table border="1">
            <caption>Hosts</caption>
            <tr>
                <th>Host</th>
                <th>Status</th>
                <th>Status Update Time</th>
                <th>Last Time Up</th>
            </tr>
            <tbody>{html_hosts}</tbody>
        </table>
    '''


def _get_html_services_report(
    services: List,
    link: str = ''
) -> str:
    """
    Generate the Services HTML report.  We assume duplicate records to be
    removed at this stage.

    :return: string html report
    """
    services = sorted(
        services,
        key=lambda service: service.get('status_update_time'),
        reverse=True)

    html_services = ''
    for service in services:
        if link:
            name = '<a href="{link}{host}">{host}</a>'.format(
                link=link,
                host=service.get('host_name')
            )
        else:
            name = service.get('host_name')

        html_services += f'''
            <tr>
                <td>{service.get('display_name')}</td>
                <td>{name}</td>
                <td>{service.get('output')}</td>
                <td>{service.get('status_update_time')}</td>
                <td>{service.get('last_time_ok')}</td>
            </tr>'''
    return f'''
        <table border="1">
            <caption>Services</caption>
            <tr>
                <th>Service</th>
                <th>Host</th>
                <th>Status</th>
                <th>Status Update Time</th>
                <th>Last Time OK</th>
            </tr>
            <tbody>{html_services}</tbody>
        </table>'''


def generate(
    hosts: List,
    services: List,
    link: str = ''
) -> str:
    """
    Generate an HTML report with the list of hosts and services
    """
    response = '<html><body>'
    response += '' if not hosts \
        else _get_html_hosts_report(hosts, link=link)
    response += '' if not services \
        else _get_html_services_report(services, link=link)
    response += '</body></html>'
    return response
