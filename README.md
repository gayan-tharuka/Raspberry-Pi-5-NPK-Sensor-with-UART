---

# Raspberry Pi 5 – NPK Sensor (RS485 UART) Reader

This project provides a Python script to read values from a **7-in-1 NPK Soil Sensor** over **RS485 UART** using a **Raspberry Pi 5**. It supports reading **Moisture**, **Temperature**, **Conductivity**, **pH**, **Nitrogen**, **Phosphorus**, and **Potassium**.

It also includes GPIO-based status LED handling and a detailed guide to resolve common issues like the infamous `No response received` error caused by UART misconfiguration or wiring issues.

---

## 📦 Features

- Reads and parses 7 environmental values from Modbus RTU sensor
- Communicates over `/dev/ttyAMA0` (PL011 UART)
- Optional GPIO LED status indicator (on GPIO 18)
- Auto handles CRC and error checking
- Setup guide and loopback test for troubleshooting

---

## 🧰 Hardware Requirements

- Raspberry Pi 5 (or compatible Pi with UART support)
- NPK 7-in-1 Soil Sensor (Modbus RTU, 4800 baud, 12–24V DC)
- RS485 to TTL module (preferably with auto direction control, e.g., MAX485)
- Power Supply (12–24V DC for sensor)
- 120Ω resistor for RS485 line termination (optional, for long cables)
- Optional: Status LED with 220Ω resistor (on GPIO 18)

---

## 🧪 Software Requirements

- Python 3.9+
- [pyserial](https://pypi.org/project/pyserial/)
- [lgpio](https://abyz.me.uk/rpi/pigpio/python.html)

Install with:

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
pip install pyserial lgpio
````

---

## ⚙️ UART Setup (Raspberry Pi OS 64-bit)

### 1. Enable PL011 UART

Edit config:

```bash
sudo nano /boot/firmware/config.txt
```

Add or modify:

```ini
[all]
enable_uart=1
dtoverlay=miniuart-bt
```

Then reboot:

```bash
sudo reboot
```

### 2. Disable Serial Console

```bash
sudo raspi-config
```

* Interface Options → Serial Port:

  * Login shell: **No**
  * Serial port hardware: **Yes**

---

## 🔌 Wiring Diagram

| Pi GPIO                 | RS485 Module         | Sensor         |
| ----------------------- | -------------------- | -------------- |
| GPIO 14 (TXD0) – Pin 8  | RX                   | A              |
| GPIO 15 (RXD0) – Pin 10 | TX                   | B              |
| GND (e.g., Pin 6)       | GND                  | GND            |
| 3.3V / 5V               | VCC                  | (RS485 module) |
| External 12–24V         | —                    | Sensor Power   |

**Optional:** Add 120Ω resistor across A and B for cables >10m.
**Status LED:** GPIO 18 (Pin 12) → 220Ω → GND

---

## 🚀 Running the Code

Clone or copy the `npk_sensor.py` file to a folder:

```bash
mkdir -p ~/project/npk
cd ~/project/npk
python3 -m venv venv
source venv/bin/activate
pip install pyserial lgpio
```

Run the script:

```bash
python3 npk_sensor.py
```

Sample output:

```
Parsed Data:
Moisture: 100.0 %
Temperature: 31.0 °C
Conductivity: 7980 µS/cm
pH: 6.3 pH
Nitrogen: 1626 mg/kg
Phosphorus: 1999 mg/kg
Potassium: 1999 mg/kg
```

---

## 🛠️ Troubleshooting: "No response received"

### ✅ Check Serial Symlink

```bash
ls -l /dev/serial*
# Should show: /dev/serial0 -> ttyAMA0
```

### ✅ Check UART Status

```bash
dmesg | grep tty
```

You should see: `ttyAMA0 at MMIO ... is a PL011`

### ✅ Loopback Test

Disconnect RS485. Connect GPIO 14 (TXD0) to GPIO 15 (RXD0):

```python
import serial
ser = serial.Serial('/dev/ttyAMA0', 4800, timeout=2)
ser.write(b'TEST')
print(ser.read(4))
ser.close()
```

Expected: `b'TEST'`

### ✅ Check Wiring

* Confirm: RS485 RO → Pi RX (GPIO 15)
* Confirm: RS485 DI → Pi TX (GPIO 14)
* Ensure proper GND between Pi, RS485 module, and sensor
* Check that sensor has 12–24V DC

### ✅ User Permissions

```bash
groups
# Ensure 'dialout' is listed

sudo usermod -a -G dialout pi
sudo reboot
```

### ✅ Baud Rate

Try changing this in the script:

```python
BAUD_RATE = 9600
```
---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Support

If you find this useful or encounter problems, feel free to open an issue or fork and contribute!

```

---

Let me know if you’d like me to:

- Add a `LICENSE` file (MIT)
- Generate a `.gitignore` file (with `.venv/`, `__pycache__/`, etc.)
- Help turn this into a Python package or web API

Would you like me to generate the full GitHub repo structure (with all files)?
```
