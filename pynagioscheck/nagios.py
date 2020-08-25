"""
.. codeauthor:: Charles Blais
"""

import logging
from typing import Dict, List
import json

import requests


class NagiosAPI(object):
    """
    Wrapper to query Nagios API
    """
    def __init__(
        self,
        url: str,
        apikey: str
    ):
        self.url = url
        self.apikey = apikey

    def _create_query(
        self,
        url: str,
        params: Dict[str, str]
    ) -> str:
        """
        For the service, create the full URL query
        using the params specified by arguments.

        :param params: key value pair where value can also be a list

        :return: string full URL
        """
        url_params = [f'apikey={self.apikey}']
        for key in params:
            if isinstance(params[key], list):
                for value in params[key]:
                    url_params.append(f'{key}={value}')
            else:
                url_params.append(f'{key}={params[key]}')
        return f'{url}?{"&".join(url_params)}'

    def query(
        self,
        params: Dict[str, str],
        prop: str = 'hoststatus'
    ) -> Dict:
        """
        Query the Nagios API

        :param params: key value pair where value can also be a list
        :param prop: type of object to query
        """
        url = self._create_query(
            '{url}/objects/{prop}'.format(
                url=self.url[:-1] if self.url.endswith("/") else self.url,
                prop=prop),
            params)
        logging.debug(url)
        response = requests.get(url)
        return json.loads(response.text)

    def get_critical_hosts(
        self,
        unchecked=True
    ) -> List:
        """
        Get all hosts that are critical

        Unchecked means getting those that have not been silenced
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
        return list(filter(
            lambda v:
                v.get('current_check_attempt', 0) ==
                v.get('max_check_attempts', 0),
            response.get('hoststatus', [])
        ))

    def get_critical_services(
        self,
        unchecked=True
    ) -> List:
        """
        Get all hosts that are critical

        Unchecked means getting those that have not been silenced
        """
        params = {
            "current_state": "in:1,2,3"
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
        return list(filter(
            lambda v:
                v.get('current_check_attempt', 0) ==
                v.get('max_check_attempts', 0),
            response.get('servicestatus', [])
        ))
