"""
..  codeauthor:: Charles Blais
"""

import pytest

from pynagioscheck.nagios import NagiosAPI


@pytest.fixture
def api():
    return NagiosAPI(
         "http://nagios-e1.seismo.nrcan.gc.ca/nagiosxi/api/v1/",
         "7s7jkoku"
    )


def test_host(api):
    response = api.get_critical_hosts()
    print(response)
    assert True


def test_services(api):
    response = api.get_critical_services()
    print(response)
    assert False