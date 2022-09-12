"""
Get data from nagios api and return lists of hosts and services with
critical and unknown states

For hosts, there are only 3 codes: up, down or unreachable
 As a result, for current states, 1 means up or down, <1 means up and
 >1 means down or unreachable

Host check URL:
https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/3/en/hostchecks.html

:author: Gloria Son December 2017
:history: 2018-02-05 Charles
    Major modification to clean up code
"""
import smtplib

import logging

import datetime

from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText

from typing import List, Union

from .models import \
    HostStatus, HostStatusCore, ServiceStatus, ServiceStatusCore

from .config import get_app_settings


def send(
    hosts: Union[List[HostStatus], List[HostStatusCore]],
    services: Union[List[ServiceStatus], List[ServiceStatusCore]],
    recipients: List[str],
) -> None:
    """
    Send an email of the html Nagios summary

    :param html: html format of summary
    :param recipients: list of emails to send email to
    """
    settings = get_app_settings()

    msg = MIMEMultipart('alternative')
    msg['Subject'] = settings.email_subject
    msg['To'] = ",".join(recipients)
    msg['From'] = settings.email_from

    hosts_count = len(hosts)
    more_host_count = (
        hosts_count - settings.max_report_hosts
        if hosts_count > settings.max_report_hosts
        else 0)
    hosts = hosts[:settings.max_report_hosts]

    services_count = len(services)
    more_service_count = (
        services_count - settings.max_report_services
        if services_count > settings.max_report_services
        else 0)
    services = services[:settings.max_report_services]

    msg.attach(MIMEText(settings.j2_status_template.render(
        now=datetime.datetime.utcnow(),
        hosts=hosts,
        services=services,
        url_status=settings.url_status,
        more_host_count=more_host_count,
        more_service_count=more_service_count,
    ), 'html'))

    logging.info(f'Sending email from SMTP: {settings.smtp_server}')
    smtp = smtplib.SMTP(settings.smtp_server)
    logging.info(f'Sending to: {msg["To"]}')
    smtp.sendmail(msg['From'], recipients, msg.as_string())
    smtp.quit()
