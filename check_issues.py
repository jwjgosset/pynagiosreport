#!/usr/bin/env python
'''
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
'''

import argparse
import json
import logging
import sys
import requests

def send_email(html, recipients):
    '''
    Send an email of the html Nagios summary

    :param html: html format of summary
    :param recipients: list of emails to send email to
    '''
    import getpass
    import socket
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart()
    msg['Subject'] = "Nagios XI Alert"
    msg['To'] = ",".join(recipients)
    html_body = MIMEText(html, 'html')
    msg.attach(html_body)
    smtp = smtplib.SMTP('mailhost')
    smtp.sendmail(
        getpass.getuser() + "@" + socket.gethostname(),
        recipients, msg.as_string())
    smtp.quit()

class NagiosAPI(object):
    '''
    Wrapper to query Nagios API
    '''
    def __init__(self, url, apikey):
       self.url = url
       self.apikey = apikey

    def _create_query(self, url, params):
        '''
        For the service, create the full URL query
        using the params specified by arguments.

        :param params: key value pair where value can also be a list
        
        :return: string full URL
        '''
        url_params = ['apikey={0}'.format(self.apikey)]
        for key in params:
            if isinstance(params[key], list):
                for value in params[key]:
                    url_params.append("{key}={value}".format(key=key, value=value))
            else:
                url_params.append("{key}={value}".format(key=key, value=params[key]))
        return "{url}?{params}".format(url=url, params="&".join(url_params))

    def query(self, params, objects="hoststatus"):
        '''
        Query the Nagios API

        :param params: key value pair where value can also be a list
        :param objects: type of object to query
        '''
        url = self._create_query(
            "{url}/objects/{objects}".format(
                url=self.url[:-1] if self.url.endswith("/") else self.url,
                objects=objects),
            params)
        logging.debug(url)
        response = requests.get(url)
        return json.loads(response.text)


def _get_status(api, config, objects):
    '''
    Process configuration check.  For each object, there is an attribute ID
    and is reference as
        @attributes : {'id': value}

    :param api: NagiosAPI object
    :param config: configuration
    :param objects: API reference
    
    :return: dict with refkey value as key
    '''
    status = {}
    # return an empty list
    if not objects in config:
        return status
    for params in config[objects]['checks']:
        params.update(config[objects]['default'])
        response = api.query(params, objects=objects)
        # we remove the first element of the response to simplify coding
        # first element is often a repeat of the "objects"
        response = response.values()[0]
        # No issues found
        if int(response['recordcount']) == 0:
            continue
        # If a record is found, the following key is the list of status (or single object)
        # we make sure its a list
        del response['recordcount']
        response = response.values()[0]
        if not isinstance(response, list):
            response = [response]
        for obj in response:
            status[obj['@attributes']['id']] = obj
    return status

def get_status_list(config):
    '''
    Get the list of status information for hosts and services
    '''
    api = NagiosAPI(config['nagiosapi'], config['apikey'])
    return (
        _get_status(api, config, 'hoststatus'),
        _get_status(api, config, 'servicestatus')
    )

def _get_html_hosts_report(hosts, link=''):
    '''
    Generate the Hosts HTML report.  We assume duplicate records to be removed at this
    stage.

    :return: string html report
    '''
    html_hosts = ''
    for host in hosts:
        if link:
            name = '<a href="{link}{host}">{host}</a>'.format(
                link=link,
                host=hosts[host].get('name')
            )
        else:
            name = hosts[host].get('name')

        html_hosts += '''
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>'''.format(
                name,
                hosts[host].get('status_text'),
                hosts[host].get('status_update_time'),
                hosts[host].get('last_time_up')
            )

    return '''
        <table border="1">
            <caption>Hosts</caption>
            <tr>
                <th>Host</th>
                <th>Status</th>
                <th>Status Update Time</th>
                <th>Last Time Up</th>
            </tr>
            <tbody>{}</tbody>
        </table>
    '''.format(html_hosts)

def _get_html_services_report(services, link=''):
    '''
    Generate the Services HTML report.  We assume duplicate records to be removed at this
    stage.

    :return: string html report
    '''
    html_services = ''
    for service in services:
        if link:
            name = '<a href="{link}{host}">{host}</a>'.format(
                link=link,
                host=services[service].get('host_name')
            )
        else:
            name = services[service].get('host_name')

        html_services += '''
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>'''.format(
                services[service].get('name'),
                name,
                services[service].get('status_text'),
                services[service].get('status_update_time'),
                services[service].get('last_time_ok')
            )
    return '''
        <table border="1">
            <caption>Services</caption>
            <tr>
                <th>Service</th>
                <th>Host</th>
                <th>Status</th>
                <th>Status Update Time</th>
                <th>Last Time OK</th>
            </tr>
            <tbody>{}</tbody>
        </table>
    '''.format(html_services)


def get_html_report(hosts, services, link=''):
    '''
    Generate an HTML report with the list of hosts and services
    '''
    response = "<html><body>"
    response += "" if not hosts else _get_html_hosts_report(hosts, link=link)
    response += "" if not services else _get_html_services_report(services, link=link)
    response += "</body></html>"
    return response


def main():
    '''Main module (use -h for instructions)'''
    # add arguments to the parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        default="config.json", help="specify a config.json file")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true", help="Verbose")
    parser.add_argument(
        "-e", "--email",
        nargs="+", action="store",
        help="send summary through email")
    args = parser.parse_args()

    # turn on logging if verbose argument is specified
    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.ERROR))

    try:
        logging.info("Load configuration %s", args.config)
        with open(args.config) as fptr:
            config = json.load(fptr)
    except IOError:
        logging.error("Cannot find configuration file")
        return 1
    except ValueError:
        logging.error("Configuration JSON format is invalid")
        return 1

    hosts, services = get_status_list(config)
    if not hosts and not services:
        logging.info("No hosts or services to report")
        return 0

    if not args.email:
        logging.warning("No email recipients defined")
        return 0
    send_email(
        get_html_report(hosts, services, link=config.get('hostlink')),
        args.email)


if __name__ == "__main__":
    sys.exit(main())
