"""
..  codeauthor:: Charles Blais
"""

import pytest

from pynagiosreport.nagios.statusfile import StatusFile


@pytest.fixture
def status() -> StatusFile:
    return StatusFile('tests/status.dat')


def test_host(status: StatusFile):
    response = status.get_critical_hosts()
    print(response)
    assert len(response) == 0


def test_services(status: StatusFile):
    response = status.get_critical_services()
    print(response)
    assert len(response) != 0
