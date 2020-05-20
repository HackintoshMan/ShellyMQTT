# coding=utf-8
import unittest
from mock import patch
import sys
import logging

from mocking.IndigoDevice import IndigoDevice
from mocking.IndigoServer import Indigo
from mocking.IndigoAction import IndigoAction

indigo = Indigo()
sys.modules['indigo'] = indigo
from Devices.Relays.Shelly_1 import Shelly_1


class Test_Shelly_1(unittest.TestCase):

    def setUp(self):
        indigo.__init__()
        self.device = IndigoDevice(id=123456, name="New Device")
        self.shelly = Shelly_1(self.device)
        logging.getLogger('Plugin.ShellyMQTT').addHandler(logging.NullHandler())

        self.device.pluginProps['address'] = "shellies/shelly1-test"
        self.device.updateStateOnServer("sw-input", False)
        self.device.updateStateOnServer("longpush", False)
        self.device.updateStateOnServer("ip-address", None)
        self.device.updateStateOnServer("mac-address", None)
        self.device.updateStateOnServer("online", False)

    def test_getSubscriptions_no_address(self):
        self.device.pluginProps['address'] = None
        self.assertListEqual([], self.shelly.getSubscriptions())

    def test_getSubscriptions(self):
        topics = [
            "shellies/announce",
            "shellies/shelly1-test/online",
            "shellies/shelly1-test/relay/0",
            "shellies/shelly1-test/input/0",
            "shellies/shelly1-test/longpush/0"
        ]
        self.assertListEqual(topics, self.shelly.getSubscriptions())

    def test_handleMessage_relay_on(self):
        self.assertTrue(self.shelly.isOff())
        self.shelly.handleMessage("shellies/shelly1-test/relay/0", "on")
        self.assertTrue(self.shelly.isOn())

    def test_handleMessage_relay_off(self):
        self.shelly.turnOn()
        self.assertTrue(self.shelly.isOn())
        self.shelly.handleMessage("shellies/shelly1-test/relay/0", "off")
        self.assertTrue(self.shelly.isOff())

    def test_handleMessage_switch_on(self):
        self.assertFalse(self.shelly.device.states['sw-input'])
        self.shelly.handleMessage("shellies/shelly1-test/input/0", "1")
        self.assertTrue(self.shelly.device.states['sw-input'])

    def test_handleMessage_switch_off(self):
        self.shelly.device.states['sw-input'] = True
        self.assertTrue(self.shelly.device.states['sw-input'])
        self.shelly.handleMessage("shellies/shelly1-test/input/0", "0")
        self.assertFalse(self.shelly.device.states['sw-input'])

    def test_handleMessage_longpush_on(self):
        self.assertFalse(self.shelly.device.states['longpush'])
        self.shelly.handleMessage("shellies/shelly1-test/longpush/0", "1")
        self.assertTrue(self.shelly.device.states['longpush'])

    def test_handleMessage_longpush_off(self):
        self.shelly.device.states['longpush'] = True
        self.assertTrue(self.shelly.device.states['longpush'])
        self.shelly.handleMessage("shellies/shelly1-test/longpush/0", "0")
        self.assertFalse(self.shelly.device.states['longpush'])

    def test_handleMessage_announce(self):
        announcement = '{"id": "shelly1-test", "mac": "aa:bb:cc:dd", "ip": "192.168.1.100", "fw_ver": "0.0.0", "new_fw": false}'
        self.shelly.handleMessage("shellies/announce", announcement)

        self.assertEqual("aa:bb:cc:dd", self.shelly.device.states['mac-address'])
        self.assertEqual("192.168.1.100", self.shelly.getIpAddress())
        self.assertEqual("0.0.0", self.shelly.getFirmware())
        self.assertFalse(self.shelly.updateAvailable())

    def test_handleMessage_online_true(self):
        self.shelly.device.states['online'] = False
        self.assertFalse(self.shelly.device.states['online'])
        self.shelly.handleMessage("shellies/shelly1-test/online", "true")
        self.assertTrue(self.shelly.device.states['online'])

    def test_handleMessage_online_false(self):
        self.shelly.device.states['online'] = True
        self.assertTrue(self.shelly.device.states['online'])
        self.shelly.handleMessage("shellies/shelly1-test/online", "false")
        self.assertFalse(self.shelly.device.states['online'])

    @patch('Devices.Shelly.Shelly.publish')
    def test_handleAction_turn_on(self, publish):
        self.shelly.turnOff()
        self.assertTrue(self.shelly.isOff())
        turnOn = IndigoAction(indigo.kDeviceAction.TurnOn)
        self.shelly.handleAction(turnOn)
        self.assertTrue(self.shelly.isOn())
        publish.assert_called_with("shellies/shelly1-test/relay/0/command", "on")

    @patch('Devices.Shelly.Shelly.publish')
    def test_handleAction_turn_off(self, publish):
        self.shelly.turnOn()
        self.assertTrue(self.shelly.isOn())
        turnOff = IndigoAction(indigo.kDeviceAction.TurnOff)
        self.shelly.handleAction(turnOff)
        self.assertTrue(self.shelly.isOff())
        publish.assert_called_with("shellies/shelly1-test/relay/0/command", "off")

    @patch('Devices.Shelly.Shelly.publish')
    def test_handleAction_status_request(self, publish):
        statusRequest = IndigoAction(indigo.kDeviceAction.RequestStatus)
        self.shelly.handleAction(statusRequest)
        publish.assert_called_with("shellies/shelly1-test/command", "update")

    @patch('Devices.Shelly.Shelly.publish')
    def test_handleAction_toggle_off_to_on(self, publish):
        self.shelly.turnOff()
        self.assertTrue(self.shelly.isOff())
        toggle = IndigoAction(indigo.kDeviceAction.Toggle)
        self.shelly.handleAction(toggle)
        self.assertTrue(self.shelly.isOn())
        publish.assert_called_with("shellies/shelly1-test/relay/0/command", "on")

    @patch('Devices.Shelly.Shelly.publish')
    def test_handleAction_toggle_on_to_off(self, publish):
        self.shelly.turnOn()
        self.assertTrue(self.shelly.isOn())
        toggle = IndigoAction(indigo.kDeviceAction.Toggle)
        self.shelly.handleAction(toggle)
        self.assertTrue(self.shelly.isOff())
        publish.assert_called_with("shellies/shelly1-test/relay/0/command", "off")
