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

import getpass
import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from typing import List


def send(
    html: str,
    recipients: List[str]
) -> None:
    """
    Send an email of the html Nagios summary

    :param html: html format of summary
    :param recipients: list of emails to send email to
    """
    msg = MIMEMultipart()
    msg['Subject'] = "Nagios XI Alert"
    msg['To'] = ",".join(recipients)
    html_body = MIMEText(html, 'html')
    msg.attach(html_body)
    smtp = smtplib.SMTP('mailhost')
    smtp.sendmail(
        getpass.getuser() + '@' + socket.gethostname(),
        recipients, msg.as_string())
    smtp.quit()
