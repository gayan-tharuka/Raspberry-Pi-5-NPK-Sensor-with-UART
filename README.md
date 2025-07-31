Raspberry Pi 5 NPK Sensor with UART
This repository provides Python code to read data from a 7-in-1 NPK soil sensor (moisture, temperature, conductivity, pH, nitrogen, phosphorus, potassium) via UART (RS485) on a Raspberry Pi 5. It includes instructions to avoid the common "No response received" error caused by UART misconfiguration or wiring issues.
Hardware Requirements

Raspberry Pi 5
7-in-1 NPK soil sensor (Modbus RTU, 4800 baud, 8N1, 12-24V DC)
RS485 to TTL module (automatic direction control, e.g., MAX485)
Power supply for the sensor (12-24V DC, check datasheet)
Wires and optional 120Ω resistor (for cables >10m)
Optional LED (on GPIO 18 with 220Ω resistor for status indication)
MicroSD card with Raspberry Pi OS (64-bit recommended)

Software Requirements

Python 3.9+
Libraries: pyserial, lgpio

Setup Instructions
1. Install Raspberry Pi OS

Download and flash the latest Raspberry Pi OS (64-bit) to a microSD card using Raspberry Pi Imager.
Boot the Raspberry Pi and complete the initial setup (set user pi, enable SSH, connect to Wi-Fi).

2. Enable UART
The NPK sensor uses UART0 (GPIO 14/TX, GPIO 15/RX) for communication. Configure the Raspberry Pi to use the PL011 UART for reliability.

Edit config.txt:
sudo nano /boot/firmware/config.txt

Add or update under [all]:
[all]
enable_uart=1
dtoverlay=miniuart-bt
# Comment out conflicting settings, e.g.:
# dtparam=uart0=on
# dtoverlay=disable-bt


enable_uart=1: Enables UART0.
dtoverlay=miniuart-bt: Assigns the mini-UART to Bluetooth, leaving PL011 for UART0 (/dev/ttyAMA0).
Save (Ctrl+O, Enter, Ctrl+X) and reboot:sudo reboot




Disable Serial Console:
sudo raspi-config


Navigate to “Interface Options” → “Serial Port.”
Select “No” for “Would you like a login shell to be accessible over serial?”
Select “Yes” for “Would you like the serial port hardware to be enabled?”
Finish and reboot.


Verify UART:
ls -l /dev/serial*

Expected: lrwxrwxrwx 1 root root 8 <date> /dev/serial0 -> ttyAMA0
dmesg | grep tty

Look for /dev/ttyAMA0 as a PL011 UART (e.g., ttyAMA0 at MMIO ... is a PL011 AXI).


3. Set Up Wiring
Connect the RS485 module and sensor to the Raspberry Pi:

Raspberry Pi to RS485 Module:
GPIO 14 (pin 8, TXD0) → RS485 DI (Driver Input)
GPIO 15 (pin 10, RXD0) → RS485 RO (Receiver Output)
GND (e.g., pin 6) → RS485 GND and sensor GND


RS485 Module to Sensor:
RS485 A → Sensor A
RS485 B → Sensor B


Power:
Sensor: 12-24V DC (check datasheet)
RS485 module: 3.3V or 5V (from Raspberry Pi or external source)


Optional: Add a 120Ω resistor across A and B for long cables (>10m).
Optional LED: Connect to GPIO 18 (pin 12) with a 220Ω resistor to GND.

Troubleshooting Tip: Use a multimeter to verify continuity. Ensure the RS485 module supports automatic direction control (no DE/RE pins). A common error is swapping RX/TX: confirm RS485 RO → Pi TX, RS485 DI → Pi RX.
4. Install Software

Update System:sudo apt update && sudo apt upgrade -y


Install Python and pip:sudo apt install python3 python3-pip python3-venv -y


Create Virtual Environment:mkdir -p ~/project/npk
cd ~/project/npk
python3 -m venv venv
source venv/bin/activate


Install Libraries:pip install pyserial lgpio



5. Run the Code

Save the code as npk_sensor.py (see repository).
Run:cd ~/project/npk
source venv/bin/activate
python3 npk_sensor.py


Expected output:NPK Sensor Test on Raspberry Pi 5 (UART)
Serial port /dev/ttyAMA0 opened successfully
Sending query: 01 03 00 00 00 07 04 08
Received 19 bytes: 01 03 0E 03 E8 01 36 1F 2C 00 3F 06 5A 07 CF 07 CF 88 57
Parsed Data:
Moisture: 100.0 %
Temperature: 31.0 °C
Conductivity: 7980 µS/cm
pH: 6.3 pH
Nitrogen: 1626 mg/kg
Phosphorus: 1999 mg/kg
Potassium: 1999 mg/kg



Troubleshooting “No response received”
If you see “No response received”:

Check UART:
Verify /dev/serial0 -> ttyAMA0:ls -l /dev/serial*


Check UART status:dmesg | grep tty




Test UART Loopback:
Disconnect RS485 module.
Connect GPIO 14 (pin 8) to GPIO 15 (pin 10).
Run:import serial
ser = serial.Serial('/dev/ttyAMA0', 4800, timeout=2)
print("Testing UART loopback...")
ser.write(b'TEST')
response = ser.read(4)
print(f"Sent: TEST, Received: {response.decode('ascii', errors='ignore')}")
ser.close()

Expected: Sent: TEST, Received: TEST


Verify Wiring:
Confirm RS485 RO → Pi TX (GPIO 14), RS485 DI → Pi RX (GPIO 15).
Check sensor power (12-24V DC).


Check Permissions:groups

Ensure dialout is listed. If not:sudo usermod -a -G dialout pi
sudo reboot


Test Baud Rate:
Edit npk_sensor.py to try BAUD_RATE = 9600 if 4800 fails.


Reinstall Libraries:pip install --force-reinstall pyserial lgpio



Data Visualization
The following bar chart visualizes sample readings (Outside, Clear Water, Fertilized Water):

{
  "type": "bar",
  "data": {
    "labels": ["Outside", "Clear Water", "Fertilized Water"],
    "datasets": [
      {
        "label": "Moisture (%)",
        "data": [0.0, 100.0, 100.0],
        "backgroundColor": "rgba(54, 162, 235, 0.8)",
        "borderColor": "rgba(54, 162, 235, 1)",
        "borderWidth": 1
      },
      {
        "label": "Temperature (°C)",
        "data": [31.3, 29.5, 31.0],
        "backgroundColor": "rgba(255, 99, 132, 0.8)",
        "borderColor": "rgba(255, 99, 132, 1)",
        "borderWidth": 1
      },
      {
        "label": "Conductivity (µS/cm)",
        "data": [0, 127, 7980],
        "backgroundColor": "rgba(75, 192, 192, 0.8)",
        "borderColor": "rgba(75, 192, 192, 1)",
        "borderWidth": 1
      },
      {
        "label": "pH",
        "data": [0, 6.2, 6.3],
        "backgroundColor": "rgba(255, 206, 86, 0.8)",
        "borderColor": "rgba(255, 206, 86, 1)",
        "borderWidth": 1
      },
      {
        "label": "Nitrogen (mg/kg)",
        "data": [0, 0, 1626],
        "backgroundColor": "rgba(153, 102, 255, 0.8)",
        "borderColor": "rgba(153, 102, 255, 1)",
        "borderWidth": 1
      },
      {
        "label": "Phosphorus (mg/kg)",
        "data": [0, 18, 1999],
        "backgroundColor": "rgba(255, 159, 64, 0.8)",
        "borderColor": "rgba(255, 159, 64, 1)",
        "borderWidth": 1
      },
      {
        "label": "Potassium (mg/kg)",
        "data": [0, 10, 1999],
        "backgroundColor": "rgba(46, 204, 113, 0.8)",
        "borderColor": "rgba(46, 204, 113, 1)",
        "borderWidth": 1
      }
    ]
  },
  "options": {
    "scales": {
      "y": {
        "beginAtZero": true,
        "title": { "display": true, "text": "Value" }
      },
      "x": {
        "title": { "display": true, "text": "Condition" }
      }
    },
    "plugins": {
      "legend": { "position": "top" },
      "title": { "display": true, "text": "NPK Sensor Measurements on Raspberry Pi 5 (UART)" }
    }
  }
}

License
This project is licensed under the MIT License. See LICENSE for details.
