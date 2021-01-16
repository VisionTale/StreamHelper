"""
Library for network operations.
"""


def is_up(host) -> bool:
    """
    Check if a host is up and running.

    :param host: hostname
    :return: whether the host is reachable
    """
    from os import system
    return True if system("ping -c 1 " + host + ' > /dev/null 2>&1') == 0 else False


def check_internet(hosts=None) -> bool:
    """
    Check all given hosts if they are up. Assumes internet connection if any one succeeds.

    Do not include local addresses!

    :param hosts: hostnames to ping to. Defaults to 1.1.1.1 and 8.8.8.8
    :return: whether any host is reachable
    """
    if hosts is None:
        hosts = ["1.1.1.1", "8.8.8.8"]
    for host in hosts:
        if is_up(host):
            return True
    return False
