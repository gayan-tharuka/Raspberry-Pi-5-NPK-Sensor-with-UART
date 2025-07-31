import serial  # For UART communication with RS485 module
import time  # For timeouts and delays
import lgpio  # For controlling GPIO pins (e.g., status LED)
from typing import Optional  # For type hints

# Configuration constants
SERIAL_PORT = "/dev/ttyAMA0"  # UART port (confirmed as /dev/serial0 -> ttyAMA0)
BAUD_RATE = 4800  # Sensor baud rate (4800 baud, 8N1 per datasheet)
TIMEOUT = 2  # 2-second timeout for reading responses
LED_PIN = 18  # GPIO 18 for status LED (set to None if not used)
QUERY_DATA = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x07, 0x04, 0x08])  # Modbus query: read 7 registers
EXPECTED_RESPONSE_LENGTH = 19  # Expected response: 1 (ID) + 1 (func) + 1 (count) + 14 (data) + 2 (CRC)

def calculate_crc(data: bytearray, length: int) -> int:
    """
    Calculate Modbus RTU CRC-16 for response validation.
    Args:
        data: Bytearray of message (excluding CRC).
        length: Number of bytes to process.
    Returns:
        CRC value as integer.
    """
    crc = 0xFFFF
    for pos in range(length):
        crc ^= data[pos]
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def initialize() -> tuple[Optional[serial.Serial], Optional[int]]:
    """
    Initialize serial port and GPIO.
    Returns:
        Tuple of (serial object, GPIO handle) or (None, None) on failure.
    """
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=TIMEOUT
        )
        print("NPK Sensor Test on Raspberry Pi 5 (UART)")
        print(f"Serial port {SERIAL_PORT} opened successfully")
    except serial.SerialException as e:
        print(f"Failed to open serial port: {e}")
        return None, None

    try:
        h = lgpio.gpiochip_open(0)
        if LED_PIN is not None:
            lgpio.gpio_claim_output(h, LED_PIN, 0)
    except Exception as e:
        print(f"Failed to initialize GPIO: {e}")
        ser.close()
        return None, None

    return ser, h

def main():
    """
    Main loop: Query sensor and print data.
    """
    ser, gpio_handle = initialize()
    if ser is None:
        return

    try:
        while True:
            ser.reset_input_buffer()  # Clear stale data
            print("Sending query:", ' '.join(f'{b:02X}' for b in QUERY_DATA))
            ser.write(QUERY_DATA)  # Send Modbus query
            ser.flush()

            start_time = time.time()
            received_data = bytearray()
            while len(received_data) < EXPECTED_RESPONSE_LENGTH and (time.time() - start_time) < TIMEOUT:
                chunk = ser.read(EXPECTED_RESPONSE_LENGTH - len(received_data))
                if chunk:
                    print(f"Received chunk: {' '.join(f'{b:02X}' for b in chunk)}")
                received_data.extend(chunk)
                time.sleep(0.01)

            if LED_PIN is not None and gpio_handle is not None:
                lgpio.gpio_write(gpio_handle, LED_PIN, 1 if len(received_data) > 0 else 0)

            if len(received_data) > 0:
                print(f"Received {len(received_data)} bytes: {' '.join(f'{b:02X}' for b in received_data)}")
            else:
                print("No response received.")
                time.sleep(3)
                continue

            if (len(received_data) == EXPECTED_RESPONSE_LENGTH and
                received_data[0] == 0x01 and
                received_data[1] == 0x03 and
                received_data[2] == 0x0E):
                received_crc = (received_data[18] << 8) | received_data[17]
                calculated_crc = calculate_crc(received_data, 17)
                if received_crc != calculated_crc:
                    print("Invalid response: CRC mismatch.")
                    time.sleep(3)
                    continue

                # Parse 7 registers (2 bytes each)
                moisture = (received_data[3] << 8) | received_data[4]
                temperature = (received_data[5] << 8) | received_data[6]
                conductivity = (received_data[7] << 8) | received_data[8]
                pH = (received_data[9] << 8) | received_data[10]
                nitrogen = (received_data[11] << 8) | received_data[12]
                phosphorus = (received_data[13] << 8) | received_data[14]
                potassium = (received_data[15] << 8) | received_data[16]

                # Print parsed data with scaling
                print("Parsed Data:")
                print(f"Moisture: {moisture / 10.0:.1f} %")
                print(f"Temperature: {temperature / 10.0:.1f} °C")
                print(f"Conductivity: {conductivity} µS/cm")
                print(f"pH: {(pH / 10.0):.1f} pH" if moisture > 0 else "pH: N/A (sensor not in medium)")
                print(f"Nitrogen: {nitrogen} mg/kg")
                print(f"Phosphorus: {phosphorus} mg/kg")
                print(f"Potassium: {potassium} mg/kg")
                print()

            else:
                print("Invalid response (wrong ID, function code, or byte count).")

            if LED_PIN is not None and gpio_handle is not None:
                lgpio.gpio_write(gpio_handle, LED_PIN, 0)

            time.sleep(3)  # Wait before next query

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
        if gpio_handle is not None:
            if LED_PIN is not None:
                lgpio.gpio_write(gpio_handle, LED_PIN, 0)
                lgpio.gpio_free(gpio_handle, LED_PIN)
            lgpio.gpiochip_close(gpio_handle)
        print("Resources cleaned up.")

if __name__ == "__main__":
    main()
