# Install dependencies: pip install python-can python-obd tkinter
import can
import obd
import time
import tkinter as tk
from threading import Thread

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

        # UI setup
        self.root = tk.Tk()
        self.root.title("OSCAROS Dashboard")
        self.root.geometry("400x200")
        self.running = True

        # Labels for displaying data
        self.rpm_label = tk.Label(self.root, text="RPM: N/A", font=("Arial", 14))
        self.rpm_label.pack(pady=10)
        self.speed_label = tk.Label(self.root, text="Speed: N/A", font=("Arial", 14))
        self.speed_label.pack(pady=10)
        self.temp_label = tk.Label(self.root, text="Coolant Temp: N/A", font=("Arial", 14))
        self.temp_label.pack(pady=10)

        # Start data update thread
        self.update_thread = Thread(target=self.update_data)
        self.update_thread.daemon = True  # Thread stops when main program exits
        self.update_thread.start()

    def read_engine_rpm(self):
        """Read engine RPM via OBD-II."""
        if not self.obd_connection:
            return None
        rpm = self.obd_connection.query(obd.commands.RPM)
        if rpm.is_null():
            return None
        return rpm.value.magnitude

    def read_speed(self):
        """Read vehicle speed via OBD-II."""
        if not self.obd_connection:
            return None
        speed = self.obd_connection.query(obd.commands.SPEED)
        if speed.is_null():
            return None
        return speed.value.magnitude

    def read_coolant_temp(self):
        """Read coolant temperature via OBD-II."""
        if not self.obd_connection:
            return None
        temp = self.obd_connection.query(obd.commands.COOLANT_TEMP)
        if temp.is_null():
            return None
        return temp.value.magnitude

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

    def update_data(self):
        """Update UI with live data."""
        while self.running:
            # Read data
            rpm = self.read_engine_rpm()
            speed = self.read_speed()
            temp = self.read_coolant_temp()

            # Update UI labels
            self.rpm_label.config(text=f"RPM: {rpm if rpm is not None else 'N/A'}")
            self.speed_label.config(text=f"Speed: {speed if speed is not None else 'N/A'} km/h")
            self.temp_label.config(text=f"Coolant Temp: {temp if temp is not None else 'N/A'} °C")

            # Sleep to avoid overwhelming the system
            time.sleep(1)

    def run(self):
        """Start the Tkinter main loop."""
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)  # Handle window close
        self.root.mainloop()

    def shutdown(self):
        """Clean up connections and stop the program."""
        self.running = False  # Stop the update thread
        if self.can_bus:
            self.can_bus.shutdown()
            print("OSCAROS: CAN bus disconnected")
        if self.obd_connection:
            self.obd_connection.close()
            print("OSCAROS: OBD-II disconnected")
        self.root.quit()  # Close the UI

# Run OSCAROS
if __name__ == "__main__":
    oscaros = OSCAROS()
    oscaros.run()