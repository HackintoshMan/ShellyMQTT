from MQTTConnector import MQTTConnector
from IndigoPlugin import IndigoPlugin


class Indigo:

    def __init__(self):
        self.server = IndigoServer()
        self.kStateImageSel = StateImages()
        self.kDeviceAction = DeviceActions()
        self.kUniversalAction = UniversalActions()
        self.activePlugin = IndigoPlugin()


class IndigoServer:

    def __init__(self):
        self.plugins = {
            "com.flyingdiver.indigoplugin.mqtt": MQTTConnector()
        }

    def getPlugin(self, identifier):
        return self.plugins.get(identifier, None)


class StateImages:

    def __init__(self):
        self.PowerOn = "PowerOn"
        self.PowerOff = "PowerOff"
        self.DimmerOn = "DimmerOn"
        self.DimmerOff = "DimmerOff"
        self.TemperatureSensor = "TemperatureSensor"
        self.TemperatureSensorOn = "TemperatureSensorOn"
        self.SensorTripped = "SensorTripped"
        self.SensorOff = "SensorOff"
        self.DoorSensorOpened = "DoorSensorOpened"
        self.DoorSensorClosed = "DoorSensorClosed"
        self.WindowSensorOpened = "WindowSensorOpened"
        self.WindowSensorClosed = "WindowSensorClosed"
        self.EnergyMeterOn = "EnergyMeterOn"
        self.EnergyMeterOff = "EnergyMeterOff"


class DeviceActions:

    def __init__(self):
        self.TurnOn = "TurnOn"
        self.TurnOff = "TurnOff"
        self.Toggle = "Toggle"
        self.RequestStatus = "RequestStatus"
        self.SetBrightness = "SetBrightness"
        self.BrightenBy = "BrightenBy"
        self.DimBy = "DimBy"


class UniversalActions:

    def __init__(self):
        self.EnergyReset = "EnergyReset"
        self.EnergyUpdate = "EnergyUpdate"

