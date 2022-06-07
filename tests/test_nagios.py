"""
..  codeauthor:: Charles Blais
"""

import pytest

from pynagiosreport.nagios import NagiosAPI


@pytest.fixture
def api() -> NagiosAPI:
    return NagiosAPI(
         "http://nagios-e1.seismo.nrcan.gc.ca/nagiosxi/api/v1/",
         "7s7jkoku",
    )


def test_host(api: NagiosAPI):
    response = api.get_critical_hosts()
    print(response)
    assert len(response) != 0


def test_services(api: NagiosAPI):
    response = api.get_critical_services()
    print(response)
    assert len(response) != 0
