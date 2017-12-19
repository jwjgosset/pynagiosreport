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
'''

import argparse
import json
import logging
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
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

#state history constants
STATE_HISTORY_URL = "objects/statehistory"
SERVICE_DESCRIPTION_KEY = "service_description"
STATE_TIME_KEY = "state_time"
OUTPUT_KEY = "output"
CURRENT_CHECK_KEY = "current_check_attempt"
MAX_CHECK_KEY = "max_check_attempts"
STATE_KEY = "state"

def send_email(html, recipients, detail):
    '''
    Send an email of the html Nagios summary

    :param html: html format of summary
    :param recipients: list of emails to send email to
    :param detail: html format of detail tables
    '''

    msg = MIMEMultipart()
    msg['Subject'] = "Nagios XI Alert"
    msg['To'] = ",".join(recipients)

    message = "<html> " + html + "<br /> <p>Details</p>"+ "<br />".join(detail) + "</html>"
    html_body = MIMEText(message, 'html')
    msg.attach(html_body)

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail('localhost', recipients, msg.as_string())
    smtp.quit()

def create_details_html(detail_summary, historylist):
    '''
    STATE HISTORY
    Format html tables for the state history query results

    :param detail_summary: long string that contains all the detail tables
    :param historylist: an entry from the api state history response
    '''
    table = ""
    host = historylist[0][HOST_NAME_KEY]
    # append row to a table of an entry
    for row in historylist:
        table += '''
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}/{}</td>
            <td>{}</td>
        </tr>
        '''.format(
            row[SERVICE_DESCRIPTION_KEY],
            row[STATE_KEY],
            row[STATE_TIME_KEY],
            row[CURRENT_CHECK_KEY],
            row[MAX_CHECK_KEY],
            row[OUTPUT_KEY])

    #add the table to the entire detail html string
    detail_summary.append('''
    <table border="1">
        <caption>{}</caption>
        <tr>
            <th>Service</th>
            <th>Status</th>
            <th>Time</th>
            <th>Checks</th>
            <th>Description</th>
        </tr>
        <tbody>{}</tbody>
    </table>
    '''.format(host, table))

def detail_query(base_url, api_key, details, detail_summary):
    '''
    STATE HISTORY
    Create the query string and get the results from the nagios api

    :param base_url: nagios api website
    :param api_key: api key to access
    :param details: list of hosts/services histories to be checked
    :param detail_summary: string that will hold the html format of
        finalized the detail summary
    '''
    #get the last hour date string
    last_hour = datetime.utcnow() - timedelta(hours=1)
    last_hour_str = last_hour.strftime("%s")

    #create the base of the query string
    base_url = "{}{}?apikey={}".format(
        base_url if base_url.endswith("/") else base_url + "/",
        STATE_HISTORY_URL,
        api_key)

    for entry in details:
        params = []
        params.append("{}={}".format("starttime", last_hour_str))
        params.append("{}=lk:{}".format(HOST_NAME_KEY, entry["host"]))
        params.append("{}=lk:{}".format(SERVICE_DESCRIPTION_KEY, entry["service"]))
        url = base_url + "&" + "&".join(params)

        try:
            #use requests to get the JSON response
            response = requests.get(url)
            response = json.loads(response.text)
            historylist = response.values()[0]

            #if there is content in the response, an html will be created
            if int(historylist[RECORDCOUNT_KEY]) > 0:
                del historylist[RECORDCOUNT_KEY]
                historylist = historylist.values()[0]
                if not isinstance(historylist, list):
                    historylist = [historylist]
                create_details_html(detail_summary, historylist)
        except requests.exceptions.ConnectionError:
            logging.error("Cannot query %s", url)

def html_format(hosts, services):
    '''
    STATUS
    Creates the html format of the status summary

    :param hosts: list of hosts with issues
    :param services: list of services with issues
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
    '''.format(host_html, service_html)
    return html

def write_soh_summary(filename, hosts, services):
    '''
    STATUS
    Writes results of hosts/services with issues into a file/stdout

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

def get_query(url, host_list, service_list, base_redirect, detail_check):
    '''
    STATUS
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
            # If the key HOST_NAME exists, it's a service
            # We convert the CURRENT_STATE to readable format
            if HOST_NAME_KEY in entry:
                redirect_link = base_redirect + entry[HOST_NAME_KEY]
                state = CURRENT_STATE_SERVICE.get(
                    entry[CURRENT_STATE_KEY],
                    "Unknown state value %s" % entry[CURRENT_STATE_KEY])
                service_list.append("{}: {} [{}] '{}' {}".format(
                    entry[HOST_NAME_KEY], entry[NAME_KEY], state,
                    entry[STATUS_UPDATE_TIME_KEY], redirect_link))
                detail_check.append({"host": entry[HOST_NAME_KEY], "service": entry[NAME_KEY]})
            else:
                redirect_link = base_redirect + entry[NAME_KEY]
                state = CURRENT_STATE_HOST.get(
                    entry[CURRENT_STATE_KEY],
                    "Unknown state value %s" % entry[CURRENT_STATE_KEY])
                host_list.append("{} [{}] '{}' {}".format(
                    entry[NAME_KEY], state, entry[STATUS_UPDATE_TIME_KEY], redirect_link))
                detail_check.append({"host": entry[NAME_KEY], "service": ""})

def create_query(config):
    '''
    STATUS
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
    detail_check = []
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
                get_query(url, host_list, service_list, base_redirect, detail_check)
            except requests.exceptions.ConnectionError:
                logging.error("Cannot query %s", url)

    return host_list, service_list, detail_check

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

    api = config["nagiosapi"]
    api_key = config["apikey"]
    hosts, services, details = create_query(config)

    detail_summary = []
    detail_query(api, api_key, details, detail_summary)
    html = ""

    write_soh_summary(args.output, hosts, services)
    if args.format:
        html = html_format(hosts, services)
        logging.info(html)
    if args.email:
        send_email(html, args.email, detail_summary)

if __name__ == "__main__":
    main()
