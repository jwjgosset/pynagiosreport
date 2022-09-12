'''
..  codeauthor:: Charles Blais
'''
import logging

from typing import List, Dict, Union

import re

from pynagiosreport.models import HostStatusCore, ServiceStatusCore

from pathlib import Path


class StatusFile:
    '''
    Handler of status.dat file parsing
    '''
    def __init__(self, filename):
        self.filename = filename
        if not Path(self.filename).exists():
            raise FileNotFoundError(f'{self.filename} not found')

    @staticmethod
    def is_critical_host(host: HostStatusCore) -> bool:
        '''
        Check if the host is critical
        '''
        return host.current_state in [1, 2]

    @staticmethod
    def is_critical_service(service: ServiceStatusCore) -> bool:
        '''
        Check if the service is critical
        '''
        return service.current_state in [2, 3]

    @staticmethod
    def is_unchecked(
        obj: Union[HostStatusCore, ServiceStatusCore]
    ) -> bool:
        '''
        Check if has to be alarmed
        '''
        if not obj.notifications_enabled:
            return False

        if obj.problem_has_been_acknowledged:
            return False

        if obj.scheduled_downtime_depth:
            return False

        return True

    @staticmethod
    def _add_object_to_host(
        obj: Dict[str, str],
        unchecked: bool,
        result: List[HostStatusCore],
    ) -> List[HostStatusCore]:
        '''
        Check the content an determine if needs ot be added
        '''
        if len(obj.keys()) == 0:  # empty object
            logging.debug('empty object, continue')
            return result

        host = HostStatusCore(**obj)
        if not StatusFile.is_critical_host(host):
            logging.debug(f'[host] {host.host_name} not critical')
            return result

        if host.current_attempt != host.max_attempts:
            logging.debug('[host]check attempt not completed')
            return result

        logging.info(f'[host] {host.host_name} critical')

        if unchecked and not StatusFile.is_unchecked(host):
            logging.debug(f'[host] {host.host_name} checked')
            return result

        result.append(host)
        return result

    def get_critical_hosts(
        self,
        unchecked: bool = True,
    ) -> List[HostStatusCore]:
        """
        Get all hosts that are critical (include unknown)

        :param bool unchecked: get those that have not been silenced
            acknowledged, or scheduled a downtime
        """
        host_pattern_start = re.compile(r'^\s*hoststatus\s*{')
        host_pattern_end = re.compile(r'^\s*}')
        attr_pattern = re.compile(r'\s*(\w+)(?:=|\s+)(.*)')

        result: List[HostStatusCore] = []

        with open(self.filename) as fp:
            obj: Dict[str, str] = {}
            in_block = False
            for line in fp:
                logging.debug(f'processing line: {line}')
                match_host = host_pattern_start.match(line)
                match_attr = attr_pattern.match(line)
                match_end = host_pattern_end.match(line)
                if line.startswith('#'):
                    continue
                elif match_host:
                    logging.debug('found start')
                    in_block = True
                elif match_end:
                    logging.debug('found end')
                    in_block = False
                    StatusFile._add_object_to_host(
                        obj, unchecked, result)
                    obj = {}
                elif in_block and match_attr:
                    attribute = match_attr.group(1)
                    value = match_attr.group(2).strip()
                    logging.debug(f'decoded {attribute}:{value}')
                    obj[attribute] = value
        return result

    @staticmethod
    def _add_object_to_service(
        obj: Dict[str, str],
        unchecked: bool,
        result: List[ServiceStatusCore],
    ) -> List[ServiceStatusCore]:
        '''
        Check the content an determine if needs ot be added
        '''
        if len(obj.keys()) == 0:  # empty object
            logging.debug('empty object, continue')
            return result

        service = ServiceStatusCore(**obj)
        if not StatusFile.is_critical_service(service):
            logging.debug(
                f'[service] {service.service_description} not critical')
            return result

        if service.current_attempt != service.max_attempts:
            logging.debug('[service] check attempt not completed')
            return result

        logging.info(f'[service] {service.service_description} critical')

        if unchecked and not StatusFile.is_unchecked(service):
            logging.info(
                f'[service] {service.service_description} checked')
            return result

        result.append(service)
        return result

    def get_critical_services(
        self,
        unchecked: bool = True,
    ) -> List[ServiceStatusCore]:
        """
        Get all service that are critical (include unknown)

        :param bool unchecked: get those that have not been silenced
            acknowledged, or scheduled a downtime
        """
        service_pattern_start = re.compile(r'^\s*servicestatus\s*{')
        service_pattern_end = re.compile(r'^\s*}')
        attr_pattern = re.compile(r'\s*(\w+)(?:=|\s+)(.*)')

        result: List[ServiceStatusCore] = []

        with open(self.filename) as fp:
            obj: Dict[str, str] = {}
            in_block = False
            for line in fp:
                logging.debug(f'processing line: {line}')
                match_service = service_pattern_start.match(line)
                match_attr = attr_pattern.match(line)
                match_end = service_pattern_end.match(line)
                if line.startswith('#'):
                    continue
                elif match_service:
                    logging.debug('found start')
                    in_block = True
                elif match_end:
                    logging.debug('found end')
                    in_block = False
                    StatusFile._add_object_to_service(
                        obj, unchecked, result)
                    obj = {}
                elif in_block and match_attr:
                    attribute = match_attr.group(1)
                    value = match_attr.group(2).strip()
                    logging.debug(f'decoded {attribute}:{value}')
                    obj[attribute] = value
        return result
