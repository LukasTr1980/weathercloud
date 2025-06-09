import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
import weathercloud_receiver

class TestSendToIoBroker(unittest.TestCase):
    def reload_module(self):
        return importlib.reload(weathercloud_receiver)

    def test_send_to_iobroker_with_auth(self):
        with patch.dict(os.environ, {'IOBROKER_USER': 'admin', 'IOBROKER_PASSWORD': 'secret'}, clear=True):
            module = self.reload_module()
            with patch('weathercloud_receiver.requests.get') as mock_get:
                mock_response = MagicMock(status_code=200)
                mock_get.return_value = mock_response

                module.send_to_iobroker('5')

                expected_url = 'http://localhost:8087/set/javascript.0.Wetterstation.Weathercloud_Regenrate?value=5&ack=true&user=admin&pass=secret'
                mock_get.assert_called_with(expected_url, timeout=10)

    def test_send_to_iobroker_from_dotenv(self):
        with patch.dict(os.environ, {}, clear=True):
            module = self.reload_module()
            with patch('weathercloud_receiver.requests.get') as mock_get:
                mock_response = MagicMock(status_code=200)
                mock_get.return_value = mock_response

                module.send_to_iobroker('10')

                expected_url = 'http://localhost:8087/set/javascript.0.Wetterstation.Weathercloud_Regenrate?value=10&ack=true&user=dotenvuser&pass=dotenvpass'
                mock_get.assert_called_with(expected_url, timeout=10)

if __name__ == '__main__':
    unittest.main()
