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
from Devices.Sensors.Shelly_HT import Shelly_HT


class Test_Shelly_HT(unittest.TestCase):

    def setUp(self):
        indigo.__init__()
        self.device = IndigoDevice(id=123456, name="New Device")
        self.shelly = Shelly_HT(self.device)
        logging.getLogger('Plugin.ShellyMQTT').addHandler(logging.NullHandler())

        self.device.pluginProps['address'] = "shellies/shelly-ht-test"
        self.device.pluginProps['temp-units'] = "C->F"
        self.device.pluginProps['temp-offset'] = "2"
        self.device.pluginProps['temp-decimals'] = "1"
        self.device.pluginProps['humidity-offset'] = "4"
        self.device.pluginProps['humidity-decimals'] = "0"

        self.device.updateStateOnServer("ip-address", None)
        self.device.updateStateOnServer("mac-address", None)
        self.device.updateStateOnServer("online", False)
        self.device.updateStateOnServer("temperature", 0)
        self.device.updateStateOnServer("humidity", 0)
        self.device.updateStateOnServer("batteryLevel", 0)

    def test_getSubscriptions(self):
        """Test getting subscriptions with a defined address."""
        topics = [
            "shellies/announce",
            "shellies/shelly-ht-test/online",
            "shellies/shelly-ht-test/sensor/temperature",
            "shellies/shelly-ht-test/sensor/humidity",
            "shellies/shelly-ht-test/sensor/battery"
        ]
        self.assertListEqual(topics, self.shelly.getSubscriptions())

    def test_handleMessage_online_true(self):
        self.shelly.device.states['online'] = False
        self.assertFalse(self.shelly.device.states['online'])
        self.shelly.handleMessage("shellies/shelly-ht-test/online", "true")
        self.assertTrue(self.shelly.device.states['online'])

    def test_handleMessage_online_false(self):
        self.shelly.device.states['online'] = True
        self.assertTrue(self.shelly.device.states['online'])
        self.shelly.handleMessage("shellies/shelly-ht-test/online", "false")
        self.assertFalse(self.shelly.device.states['online'])

    def test_handleMessage_temperature(self):
        self.shelly.handleMessage("shellies/shelly-ht-test/sensor/temperature", "43")
        self.assertAlmostEqual(111.4, self.shelly.device.states['temperature'])
        self.assertEqual("111.4 °F", self.shelly.device.states_meta['temperature']['uiValue'])

    def test_handleMessage_humidity(self):
        self.shelly.handleMessage("shellies/shelly-ht-test/sensor/humidity", "60")
        self.assertAlmostEqual(64, self.shelly.device.states['humidity'])
        self.assertEqual("64%", self.shelly.device.states_meta['humidity']['uiValue'])

    def test_handleMessage_humidity_with_invalid_offset(self):
        self.device.pluginProps['humidity-offset'] = "4a"
        self.assertRaises(ValueError, self.shelly.handleMessage("shellies/shelly-ht-test/sensor/humidity", "60"))

    def test_handleMessage_battery(self):
        self.shelly.handleMessage("shellies/shelly-ht-test/sensor/battery", "94")
        self.assertEqual("94", self.shelly.device.states['batteryLevel'])

    def test_update_state_image_on(self):
        self.shelly.device.states['online'] = True
        self.shelly.updateStateImage()
        self.assertEqual(indigo.kStateImageSel.TemperatureSensorOn, self.shelly.device.image)

    def test_update_state_image_off(self):
        self.shelly.device.states['online'] = False
        self.shelly.updateStateImage()
        self.assertEqual(indigo.kStateImageSel.TemperatureSensor, self.shelly.device.image)
