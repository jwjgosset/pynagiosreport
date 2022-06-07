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

from typing import List

from .models import HostStatus, ServiceStatus

from .config import get_app_settings


def send(
    hosts: List[HostStatus],
    services: List[ServiceStatus],
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

    msg.attach(MIMEText(settings.j2_status_template.render(
        now=datetime.datetime.utcnow(),
        hosts=hosts,
        services=services,
        url_status=settings.url_status,
    ), 'html'))

    logging.info(f'Sending email from SMTP: {settings.smtp_server}')
    smtp = smtplib.SMTP(settings.smtp_server)
    logging.info(f'Sending to: {msg["To"]}')
    smtp.sendmail(msg['From'], recipients, msg.as_string())
    smtp.quit()
