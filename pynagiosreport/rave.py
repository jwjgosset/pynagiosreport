'''
..  codeauthor:: Charles Blais
'''
from typing import List, Union

from .models import \
    HostStatus, HostStatusCore, ServiceStatus, ServiceStatusCore

from pyravealert.inbound import \
    generate, Status, Category, Parameter, send as send_rave

from .config import get_app_settings


def get_description(
    hosts: Union[List[HostStatus], List[HostStatusCore]],
    services: Union[List[ServiceStatus], List[ServiceStatusCore]],
) -> str:
    '''
    Generate description based on hosts/services
    '''
    settings = get_app_settings()

    hosts_count = len(hosts)
    more_host_count = (
        hosts_count - settings.max_report_hosts
        if hosts_count > settings.max_report_hosts
        else 0)
    hosts_min = hosts[:settings.max_report_hosts]

    services_count = len(services)
    more_service_count = (
        services_count - settings.max_report_services
        if services_count > settings.max_report_services
        else 0)
    services_min = services[:settings.max_report_services]

    # Start description for hosts
    description = 'The following hosts are critical:\n'
    if hosts_count == 0:
        description += '- No hosts are critical\n'
    else:
        for host in hosts_min:
            description += (
                f'- {host.host_name} since '
                f'{host.last_time_up.strftime("%Y-%m-%d %H:%M")}\n'
            )
        if more_host_count:
            description += f'... {more_host_count} more hosts critical\n'

    # Start description for services
    description += '\nThe following services are critical:\n'
    if services_count == 0:
        description += '- No services are critical'
    else:
        for service in services_min:
            description += (
                f'- {service.host_name}/{service.display_name} since '
                f'{service.last_time_ok.strftime("%Y-%m-%d %H:%M")}\n'
            )
        if more_service_count:
            description += f'... {more_service_count} more services critical\n'
    return description


def send(
    hosts: Union[List[HostStatus], List[HostStatusCore]],
    services: Union[List[ServiceStatus], List[ServiceStatusCore]],
) -> None:
    '''
    Prepare nagios update by Rave
    '''
    settings = get_app_settings()

    hosts_count = len(hosts)
    services_count = len(services)

    # Start description for hosts
    description = get_description(hosts, services)
    instruction = f'Check {settings.url} for details'

    alert = generate(
        status=Status.actual,
        event='Nagios XI Notification',
        category=Category.infra,
        headline=(
            f'Nagios XI Notification - {hosts_count} '
            f'hosts, {services_count} services'
        ),
        description=description,
        instruction=instruction,
        parameter=[Parameter(
            valueName='layer:CHIS:source',
            value='nagios',
        )],
        web=settings.url,
    )
    send_rave(
        alert,
        settings.rave_url,
        settings.rave_username,
        settings.rave_password)
