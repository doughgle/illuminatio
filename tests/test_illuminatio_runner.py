import pytest
from unittest.mock import MagicMock, patch
from illuminatio.illuminatio_runner import (
    build_result_string,
    extract_results_from_nmap,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            {
                "port": "80",
                "target": "test",
                "should_be_blocked": False,
                "was_blocked": False,
            },
            "Test test:80 succeeded\nCould reach test on port 80. Expected target to be reachable",
        ),
        (
            {
                "port": "80",
                "target": "test",
                "should_be_blocked": False,
                "was_blocked": True,
            },
            "Test test:80 failed\nCouldn't reach test on port 80. Expected target to be reachable",
        ),
        (
            {
                "port": "80",
                "target": "test",
                "should_be_blocked": True,
                "was_blocked": False,
            },
            "Test test:-80 failed\nCould reach test on port 80. Expected target to not be reachable",
        ),
        (
            {
                "port": "80",
                "target": "test",
                "should_be_blocked": True,
                "was_blocked": True,
            },
            "Test test:-80 succeeded\nCouldn't reach test on port 80. Expected target to not be reachable",
        ),
    ],
)
def test_build_result_string(test_input, expected):
    assert build_result_string(**test_input) == expected


def create_nmap_mock(hosts: list):
    """Create a mock nmap scanner without requiring the actual nmap binary"""
    nmap_mock = MagicMock()
    nmap_mock.all_hosts = MagicMock(return_value=hosts)
    nmap_mock._scan_result = MagicMock(return_value={"scan"})
    if len(hosts) > 0:
        # Setup host access via dictionary-style lookup
        host_mock = MagicMock()
        host_mock.all_protocols = MagicMock(return_value=["tcp"])

        # Setup TCP port access
        tcp_dict = MagicMock()
        tcp_dict.keys = MagicMock(return_value=[80])
        host_mock.__getitem__.side_effect = (
            lambda key: tcp_dict if key == "tcp" else MagicMock()
        )

        # Setup tcp method
        host_mock.tcp = MagicMock(
            return_value={"state": "open", "reason": "syn-ack", "name": "http"}
        )

        # Make host accessible via dictionary-style lookup on nmap_mock
        nmap_mock.__getitem__.side_effect = (
            lambda key: host_mock if key in hosts else MagicMock()
        )

    return nmap_mock


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            {"hosts": [], "port_on_nums": {}, "target": "test"},
            {
                "": {
                    "error": "Found 0 hosts in nmap results, expected 1.",
                    "success": False,
                }
            },
        ),
        (
            {
                "hosts": ["123.321.123.321"],
                "port_on_nums": {"80": "80"},
                "target": "test",
            },
            {
                "80": {
                    "nmap-state": "open",
                    "string": "Test test:80 succeeded\n"
                    "Could reach test on port 80. Expected target to be "
                    "reachable",
                    "success": True,
                }
            },
        ),
        (
            {
                "hosts": ["123.321.123.321"],
                "port_on_nums": {"80": "-80"},
                "target": "test",
            },
            {
                "-80": {
                    "nmap-state": "open",
                    "string": "Test test:-80 failed\n"
                    "Could reach test on port 80. Expected target to not be "
                    "reachable",
                    "success": False,
                }
            },
        ),
        (
            {"hosts": ["::1"], "port_on_nums": {"80": "-80"}, "target": "test"},
            {
                "-80": {
                    "nmap-state": "open",
                    "string": "Test test:-80 failed\n"
                    "Could reach test on port 80. Expected target to not be "
                    "reachable",
                    "success": False,
                }
            },
        ),
    ],
)
@patch("nmap.PortScanner", new_callable=MagicMock)
def test_extract_results_from_nmap(mock_port_scanner, test_input, expected):
    # Replace the import of nmap.PortScanner with our mock
    hosts = test_input.pop("hosts")
    test_input["nmap_res"] = create_nmap_mock(hosts)
    assert extract_results_from_nmap(**test_input) == expected
