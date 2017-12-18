# Nagios Host and Service Issues Summary

## Introduction
The following python script queries the Nagios API for hosts that are DOWN and UNREACHABLE and services that are in CRITICAL or UNKNOWN statuses. 

For more information on host checks:

    https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/3/en/hostchecks.html

## Installation
Ensure that the following libraries are installed beforehand:
- requests

## Usage
The command to run the program is:

    python check_issues.py [-c config_json_name] [-o output_txt_file] [-e list of email recipients] [-v] [-f]

The additional specifications are:

    -c : specify a separate configuration json
    -o : write the results to a specified text file,
         the default is output to stdout
    -e : send an email with the summaries to a list of recipients
    -v : verbose
    -f : format summary into html tables

## Configuration File Formatting
If a configuration file is specified the following fields are required:

    "nagiosapi": [string] basic website URL (most likely shouldn't change)
    "apikey": [string] specific to each user, can be found under Account Information on the Nagios website
    "redirect": [string] actual Nagios website, host will be specified later to go to page with the immediate problem

Regex types of expressions according to the Nagios API are used in the next fields:

    "lk:{word}" - matches anything that contains {word}
    "in: {num1},{num2}" = matches anything in the range of {num1} and {num2}

The next two required fields follow a similar structure:

    "objects/hoststatus": [object]
        "default": [object]
        "checks": [list of objects]
    "objects/servicestatus": [object]
        "default": [object]
        "checks": [list of objects]

The "default field should contain:

    "problem_acknowledged": [string] either "0" or "1"
    "notifications_enabled": [string] either "0" or "1"
    "current_state": [string] range or number specifying which state to check (eg. "in:1,2" checks for 1 to 2)

Any of the fields within each object in "checks" can be a list or a single string.

For "objects/hoststatus" within "checks", each object should have:

    "name": name of host to check (eg. "lk:CN")

For "objects/servicestatus" within "checks", each object should have:

    "host_name": name of host to check (eg. "lk:CN")
    "name": name of service to check (eg. "lk:VEC")