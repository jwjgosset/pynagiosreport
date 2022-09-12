"""
..  codeauthor:: Charles Blais
"""

import pytest

from pynagiosreport.nagios.statusfile import StatusFile

from pynagiosreport.rave import get_description


@pytest.fixture
def status() -> StatusFile:
    return StatusFile('tests/status.dat')


def test_description(status: StatusFile):
    hosts = status.get_critical_hosts()
    services = status.get_critical_services()
    desc = get_description(hosts, services)
    print(desc)
    assert len(desc) > 0
