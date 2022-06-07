"""
.. codeauthor:: Charles Blais
"""

import logging

from typing import Dict, List

import json

import requests

from pydantic.error_wrappers import ValidationError

from .models import HostStatus, ServiceStatus


class NagiosAPI(object):
    """
    Wrapper to query Nagios API
    """
    def __init__(
        self,
        url: str,
        apikey: str,
    ):
        self.url = url[:-1] if url.endswith("/") else url
        self.apikey = apikey

    def query(
        self,
        params: Dict[str, str],
        prop: str = 'hoststatus',
    ) -> Dict:
        """
        Query the Nagios API

        :param params: key value pair where value can also be a list
        :param prop: type of object to query
        """
        params.update({'apikey': self.apikey})
        response = requests.get(f'{self.url}/objects/{prop}', params=params)
        return response.json()

    def get_critical_hosts(
        self,
        unchecked: bool = True,
    ) -> List[HostStatus]:
        """
        Get all hosts that are critical (include unknown)

        :param bool unchecked: get those that have not been silenced
            acknowledged, or scheduled a downtime
        """
        params = {
            "current_state": "in:1,2"
        }
        if unchecked:
            params.update({
                "problem_acknowledged": "0",
                "notifications_enabled": "1",
                "scheduled_downtime_depth": "0"
            })

        response = self.query(params, prop='hoststatus')
        if 'error' in response:
            logging.error(response)
            return []
        if int(response.get('recordcount', 0)) == 0:
            logging.info(f'No data found in query {json.dumps(params)}')
            return []

        # convert the object and return only those that should alert
        hosts: List[HostStatus] = []
        for h in response.get('hoststatus', []):
            try:
                hoststatus = HostStatus(**h)
            except ValidationError as err:
                logging.error(f'Error converting:\n{err}\nDetailed:\n{h}')
                raise err
            if (
                hoststatus.current_check_attempt
                == hoststatus.max_check_attempts
            ):
                hosts.append(hoststatus)
        return hosts

    def get_critical_services(
        self,
        unchecked: bool = True,
    ) -> List[ServiceStatus]:
        """
        Get all services that are critical

        :param bool unchecked: get those that have not been silenced
            acknowledged, or scheduled a downtime
        """
        params = {
            "current_state": "in:2,3"
        }
        if unchecked:
            params.update({
                "problem_acknowledged": "0",
                "notifications_enabled": "1",
                "scheduled_downtime_depth": "0"
            })

        response = self.query(params, prop='servicestatus')
        if 'error' in response:
            logging.error(response)
            return []
        if int(response.get('recordcount', 0)) == 0:
            logging.info(f'No data found in query {json.dumps(params)}')
            return []

        # convert the object and return only those that should alert
        services: List[ServiceStatus] = []
        for h in response.get('servicestatus', []):
            try:
                servicestatus = ServiceStatus(**h)
            except ValidationError as err:
                logging.error(f'Error converting:\n{err}\nDetailed:\n{h}')
                raise err
            if (
                servicestatus.current_check_attempt
                == servicestatus.max_check_attempts
            ):
                services.append(servicestatus)
        return services
