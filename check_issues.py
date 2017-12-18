#!/usr/bin/env python
'''
Get data from nagios api and return lists of hosts and services with
critical and unknown states

For hosts, there are only 3 codes: up, down or unreachable
 As a result, for current states, 1 means up or down, <1 means up and
 >1 means down or unreachable

Host check URL:
https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/3/en/hostchecks.html


:author: Gloria Son
'''

import argparse
import json
import logging
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

RECORDCOUNT_KEY = "recordcount"
NAME_KEY = "name"
HOST_NAME_KEY = "host_name"
STATUS_UPDATE_TIME_KEY = "status_update_time"
CURRENT_STATE_KEY = "current_state"
CURRENT_STATE_HOST = {
    "0" : "UP",
    "1" : "DOWN",
    "2" : "UNREACHABLE"
}
CURRENT_STATE_SERVICE = {
    "0" : "OK",
    "1" : "WARNING",
    "2" : "CRITICAL",
    "3" : "UNKNOWN"
}

def send_email(html, recipients):
    '''
    Send an email of the Nagios summary

    :param html: html format of summary
    '''

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Nagios XI Alert"
    msg['To'] = ",".join(recipients)

    html_body = MIMEText(html, 'html')
    msg.attach(html_body)

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail('localhost', recipients, msg.as_string())
    smtp.quit()

def html_format(hosts, services):
    '''
    Creates the html format of the summary
    '''
    host_html = ""
    service_html = ""
    for host in hosts:
        name = host[0:host.index("[")]
        status = host[host.index("[")+1:host.index("]")]
        status_time = host[host.index("'")+1:host.rfind("'")]
        link = host[host.index("http"):]
        host_html += '''
            <tr>
                <td><a href={}>{}</a></td>
                <td>{}</td>
                <td>{}</td>
            </tr>'''.format(link, name, status, status_time)

    for service in services:
        host_name = service[0:service.index(":")]
        name = service[service.index(":")+1:service.index("[")]
        status = service[service.index("[")+1:service.index("]")]
        status_time = service[service.index("'")+1:service.rfind("'")]
        link = service[service.index("http"):]
        service_html += '''
            <tr>
                <td><a href={}>{}</a></td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>'''.format(link, host_name, name, status, status_time)

    html = '''
    <html>
        <table border="1">
            <caption>Host Issues</caption>
            <tr>
                <th>Host</th>
                <th>Status</th>
                <th>Status Update Time</th>
            </tr>
            <tbody> {} </tbody>
        </table>
        <br />
        <table border="1">
            <caption>Service Issues</caption>
            <tr>
                <th>Host</th>
                <th>Service</th>
                <th>Status</th>
                <th>Status Update Time</th>
            </tr>
            <tbody> {} </tbody>
        </table>
    </html>
    '''.format(host_html, service_html)
    return html

def write_soh_summary(filename, hosts, services):
    '''
    Writes results of hosts/services with issues into a file

    :param filename: file to write list of hosts/services to
    :param hosts: list of hosts with issues
    :param servies: list of services with issues
    '''
    if not hasattr(filename, "write"):
        file_opened = True
        fptr = open(filename, "w")
    else:
        file_opened = False
        fptr = filename

    # write hosts/services into a text file or stdout if lists aren't empty
    if hosts:
        fptr.write("HOSTS \n==========\n")
        fptr.write("\n".join(hosts) + "\n")

    if services:
        fptr.write("\nSERVICES \n==========\n")
        fptr.write("\n".join(services) + "\n")

    if file_opened:
        fptr.close()


def get_query(url, host_list, service_list, base_redirect):
    '''
    Retrieves data from nagios api and adds entries to appropriate host/service list

    :param url: URL for request to nagios api
    :param host_list: list of hosts with issues
    :param service_list: list of services with issues
    :param api_url: either hoststatus or servicestatus
    '''
    # retrieve data from nagios api and convert into parsable format
    response = requests.get(url)
    response = json.loads(response.text)
    statuslist = response.values()[0]
    logging.debug(statuslist)

    # add hosts/services with issues to respective lists
    if int(statuslist[RECORDCOUNT_KEY]) > 0:
        del statuslist[RECORDCOUNT_KEY]
        statuslist = statuslist.values()[0]
        if not isinstance(statuslist, list):
            statuslist = [statuslist]

        for entry in statuslist:
            # If the key HOST_NAME exists, its a service
            # We convert the CURRENT_STATE to readable format
            if HOST_NAME_KEY in entry:
                redirect_link = base_redirect + entry[HOST_NAME_KEY]
                state = CURRENT_STATE_SERVICE.get(
                    entry[CURRENT_STATE_KEY],
                    "Unknown state value %s" % entry[CURRENT_STATE_KEY])
                service_list.append("{}: {} [{}] '{}' {}".format(
                    entry[HOST_NAME_KEY], entry[NAME_KEY], state,
                    entry[STATUS_UPDATE_TIME_KEY], redirect_link))
            else:
                redirect_link = base_redirect + entry[NAME_KEY]
                state = CURRENT_STATE_HOST.get(
                    entry[CURRENT_STATE_KEY],
                    "Unknown state value %s" % entry[CURRENT_STATE_KEY])
                host_list.append("{} [{}] '{}' {}".format(
                    entry[NAME_KEY], state, entry[STATUS_UPDATE_TIME_KEY], redirect_link))

def create_query(config):
    '''
    Creates query string and gets response request from nagios api

    :param config: configuration
    :param api_url: configuration key and API post URL

    :return: list of hosts/services with issues
    '''
    # create base url component to be appended later and remove unecessary fields
    base_url = config["nagiosapi"]
    base_key = "apikey="+ config["apikey"]
    base_redirect = config["redirect"]
    host_list = []
    service_list = []
    del config["nagiosapi"], config["apikey"], config["redirect"]

    # parse through the service and host objects in the configuration file
    for api_url in config:
        #create base_params list and add the base url
        base_params = []
        base_params.append("{}{}?{}".format(
            base_url if base_url.endswith("/") else base_url + "/",
            api_url,
            base_key))

        # parse through default parameters and add to base_params list
        for key in config[api_url]["default"]:
            base_params.append("{}={}".format(key, config[api_url]["default"][key]))

        # iterate through each of the check entries
        for check in config[api_url]["checks"]:
            # add parameters to be added to the URL string based on fields in check entries
            params = []
            for key in check:
                if isinstance(check[key], list):
                    for value in check[key]:
                        params.append("{}={}".format(key, value))
                else:
                    params.append("{}={}".format(key, check[key]))

            # creating URL to be used for request
            url = "&".join(base_params) + "&" + "&".join(params)
            logging.info("Querying: " + url)

            try:
                get_query(url, host_list, service_list, base_redirect)
            except requests.exceptions.ConnectionError:
                logging.error("Cannot query %s", url)

    return host_list, service_list

def main():
    '''main'''
    # add arguments to the parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.json", help="specify a config.json file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
    parser.add_argument("-o", "--output", default=sys.stdout,
                        help="Output file with Nagios SOH issues (default: stdout)")
    parser.add_argument("-f", "--format", action="store_true", help="write summary in html format")
    parser.add_argument("-e", "--email", nargs="+", action="store",
                        help="send summary through email")
    args = parser.parse_args()

    # turn on logging if verbose argument is specified
    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.WARNING))

    try:
        logging.info("Getting ready to fetch JSON data")
        with open(args.config) as fptr:
            logging.info("Fetching JSON data")
            config = json.load(fptr)
    except IOError:
        logging.error("Cannot find configuration file")
        sys.exit(1)
    except ValueError:
        logging.error("Configuration JSON format is invalid")
        sys.exit(1)

    logging.info("Obtained JSON data")
    hosts, services = create_query(config)
    html = ""

    write_soh_summary(args.output, hosts, services)
    if args.format:
        html = html_format(hosts, services)
        logging.info(html)
    if args.email:
        send_email(html, args.email)

if __name__ == "__main__":
    main()
