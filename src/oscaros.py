# Install dependencies: pip install python-can python-obd
import can
import obd
import time

class OSCAROS:
    def __init__(self):
        """Initialize OSCAROS with CAN and OBD connections."""
        # CAN setup (for engine control)
        try:
            self.can_bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000)
            print("OSCAROS: CAN bus connected")
        except Exception as e:
            print(f"OSCAROS: CAN setup failed - {e}")
            self.can_bus = None

        # OBD setup (for diagnostics)
        try:
            self.obd_connection = obd.OBD()  # Auto-detects OBD-II port
            if self.obd_connection.is_connected():
                print("OSCAROS: OBD-II connected")
            else:
                print("OSCAROS: OBD-II not found")
                self.obd_connection = None
        except Exception as e:
            print(f"OSCAROS: OBD setup failed - {e}")
            self.obd_connection = None

    def read_engine_rpm(self):
        """Read engine RPM via OBD-II (diagnostics)."""
        if not self.obd_connection:
            return None
        rpm = self.obd_connection.query(obd.commands.RPM)
        if rpm.is_null():
            print("OSCAROS: No RPM data")
            return None
        print(f"OSCAROS: Engine RPM - {rpm.value.magnitude}")
        return rpm.value.magnitude

    def read_can_sensor(self, arbitration_id=0x201):
        """Read raw CAN data (e.g., throttle sensor)."""
        if not self.can_bus:
            return None
        try:
            message = self.can_bus.recv(timeout=1.0)
            if message and message.arbitration_id == arbitration_id:
                print(f"OSCAROS: CAN data - {message.data.hex()}")
                return message.data
            return None
        except Exception as e:
            print(f"OSCAROS: CAN read error - {e}")
            return None

    def send_engine_command(self, arbitration_id=0x300, data=bytearray([0x01])):
        """Send a command via CAN (e.g., throttle control)."""
        if not self.can_bus:
            return False
        msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
        try:
            self.can_bus.send(msg)
            print(f"OSCAROS: Sent command to ID {arbitration_id}")
            return True
        except Exception as e:
            print(f"OSCAROS: Command error - {e}")
            return False

    def shutdown(self):
        """Clean up connections."""
        if self.can_bus:
            self.can_bus.shutdown()
            print("OSCAROS: CAN bus disconnected")
        if self.obd_connection:
            self.obd_connection.close()
            print("OSCAROS: OBD-II disconnected")

# Test OSCAROS
if __name__ == "__main__":
    oscaros = OSCAROS()

    # Read diagnostics (RPM)
    for _ in range(3):
        oscaros.read_engine_rpm()
        time.sleep(1)

    # Read raw CAN data (simulated throttle)
    for _ in range(3):
        oscaros.read_can_sensor()
        time.sleep(1)

    # Send a safe test command (e.g., dummy throttle signal)
    oscaros.send_engine_command(data=bytearray([0x01]))  # Minimal value for safety

    # Shut down
    oscaros.shutdown()