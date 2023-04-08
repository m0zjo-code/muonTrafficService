import sys
import glob
import serial
import string
import random
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
__VERSION__ = "0.0.1"
DEFAULT_BAUD = 9600
NODE_NAME = "NoNameSet"


# Random ID Generator
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# MQTT Definitions
MQTT_SERVER = "broker.hivemq.com"
MQTT_TCP_PORT = 1883
MQTT_QOS = 0
if NODE_NAME == "NoNameSet":
    MQTT_PREAMBLE = "MUON0_" + id_generator(6)
else:
    MQTT_PREAMBLE = "MUON0_" + str(NODE_NAME)


def serial_ports():
    # Found from: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
    # Updated to conform to PEP8
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (j + 1) for j in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# Define lines to ignore from detector
charFilter = [int.from_bytes(bytes("#", 'ascii'), "big"), int.from_bytes(b"\xff", "big")]


def prepare_sample(input_line):
    input_line = input_line.strip()
    input_line = input_line.replace(" ", ",")
    timestamp_dt = datetime.now(timezone.utc)
    input_line = MQTT_PREAMBLE + "," + timestamp_dt.strftime('%Y-%m-%dT%H:%M:%S.%f') + "," + input_line
    return input_line


if __name__ == '__main__':
    print("---- Muon Traffic Monitor V%s ----" % __VERSION__)
    print("---- M0ZJO - 2023 ----")

    portsFree = serial_ports()

    print("Available Ports:")
    for portID in range(0, len(portsFree)):
        print("%i | %s" % (portID, portsFree[portID]))
    cwPort = int(input("Please select the CW Unit Port:"))

    if cwPort <= (len(portsFree) - 1):
        print("Selected:", portsFree[cwPort])
    else:
        print("Invalid COM port selected - Exiting")
        sys.exit(1)

    # Attempt to open port
    ser = serial.Serial()
    ser.baudrate = DEFAULT_BAUD
    ser.port = portsFree[cwPort]
    ser.bytesize = 8
    ser.parity = 'N'
    ser.stopbits = 1
    ser.open()

    # Connect to MQTT Broker
    client = mqtt.Client()
    client.connect(MQTT_SERVER, port=MQTT_TCP_PORT)

    while True:
        line = ser.readline()
        if line[0] not in charFilter:
            try:
                line = prepare_sample(line.decode("ascii"))
                client.publish("M0ZJO/teststream", line, qos=MQTT_QOS)
                print(line)
            except Exception as e:
                print(f"\n  **Problem attempting to process: {e}")
                pass
