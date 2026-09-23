import socket
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from plugin.src.main.network import addresses, whitelist
from plugin.src.main.settings import read_config


class NetworkTests(unittest.TestCase):
    def test_development_defaults(self):
        config = read_config('port-config.yaml')
        self.assertEqual(addresses(config), ['0.0.0.0'])
        self.assertFalse(config['enable_whitelist'])
        self.assertEqual(whitelist(config), set())

    def test_standard_selects_tunnel_ipv4(self):
        sample = {'wg0': [SimpleNamespace(family=socket.AF_INET, address='10.4.0.1')],
            'tailscale0': [SimpleNamespace(family=socket.AF_INET, address='100.64.0.1')],
            'eth0': [SimpleNamespace(family=socket.AF_INET, address='192.168.1.3')]}
        with patch('psutil.net_if_addrs', return_value=sample):
            self.assertEqual(addresses({'policy': 'standard'}), ['10.4.0.1', '100.64.0.1'])

    def test_configured_whitelist_accepts_ipv4_and_rejects_ipv6(self):
        self.assertEqual(whitelist({'whitelist': '127.0.0.1, 10.0.0.2'}),
                         {'127.0.0.1', '10.0.0.2'})
        with self.assertRaises(ValueError):
            whitelist({'whitelist': '::1'})
