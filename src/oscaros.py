# Install dependencies: pip install python-can python-obd tkinter
import can
import obd
import time
import tkinter as tk
from threading import Thread
from datetime import datetime

class OSCAROS:
    def __init__(self):
        """Initialize OSCAROS with CAN and OBD connections."""
        # CAN setup
        try:
            self.can_bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000)
            print("OSCAROS: CAN bus connected")
        except Exception as e:
            print(f"OSCAROS: CAN setup failed - {e}")
            self.can_bus = None

        # OBD setup
        try:
            self.obd_connection = obd.OBD()
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
        self.root.geometry("400x450")  # Increased for more data and button
        self.running = True

        # Labels for displaying data
        self.rpm_label = tk.Label(self.root, text="RPM: N/A", font=("Arial", 12))
        self.rpm_label.pack(pady=5)
        self.speed_label = tk.Label(self.root, text="Speed: N/A", font=("Arial", 12))
        self.speed_label.pack(pady=5)
        self.temp_label = tk.Label(self.root, text="Coolant Temp: N/A", font=("Arial", 12))
        self.temp_label.pack(pady=5)
        self.throttle_label = tk.Label(self.root, text="Throttle Position: N/A", font=("Arial", 12))
        self.throttle_label.pack(pady=5)
        self.fuel_label = tk.Label(self.root, text="Fuel Level: N/A", font=("Arial", 12))
        self.fuel_label.pack(pady=5)
        self.intake_label = tk.Label(self.root, text="Intake Air Temp: N/A", font=("Arial", 12))
        self.intake_label.pack(pady=5)
        self.can_throttle_label = tk.Label(self.root, text="CAN Throttle (ID 0x201): N/A", font=("Arial", 12))
        self.can_throttle_label.pack(pady=5)
        self.can_steering_label = tk.Label(self.root, text="CAN Steering (ID 0x202): N/A", font=("Arial", 12))
        self.can_steering_label.pack(pady=5)

        # Write command button
        self.write_button = tk.Button(self.root, text="Send Test Throttle Command (ID 0x300)", command=self.send_test_command)
        self.write_button.pack(pady=10)

        # CAN logging setup
        self.log_file = open(f"oscaros_can_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w")
        self.log_file.write("Timestamp, Arbitration ID, Data, Action\n")

        # Start data update thread
        self.update_thread = Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()

    def read_engine_rpm(self):
        """Read engine RPM via OBD-II."""
        if not self.obd_connection:
            return None
        rpm = self.obd_connection.query(obd.commands.RPM)
        return rpm.value.magnitude if not rpm.is_null() else None

    def read_speed(self):
        """Read vehicle speed via OBD-II."""
        if not self.obd_connection:
            return None
        speed = self.obd_connection.query(obd.commands.SPEED)
        return speed.value.magnitude if not speed.is_null() else None

    def read_coolant_temp(self):
        """Read coolant temperature via OBD-II."""
        if not self.obd_connection:
            return None
        temp = self.obd_connection.query(obd.commands.COOLANT_TEMP)
        return temp.value.magnitude if not temp.is_null() else None

    def read_throttle_position(self):
        """Read throttle position via OBD-II."""
        if not self.obd_connection:
            return None
        throttle = self.obd_connection.query(obd.commands.THROTTLE_POS)
        return throttle.value.magnitude if not throttle.is_null() else None

    def read_fuel_level(self):
        """Read fuel level via OBD-II."""
        if not self.obd_connection:
            return None
        fuel = self.obd_connection.query(obd.commands.FUEL_LEVEL)
        return fuel.value.magnitude if not fuel.is_null() else None

    def read_intake_air_temp(self):
        """Read intake air temperature via OBD-II."""
        if not self.obd_connection:
            return None
        intake = self.obd_connection.query(obd.commands.INTAKE_TEMP)
        return intake.value.magnitude if not intake.is_null() else None

    def read_can_sensor(self, arbitration_id):
        """Read raw CAN data for a specific arbitration ID."""
        if not self.can_bus:
            return None
        try:
            message = self.can_bus.recv(timeout=0.1)
            if message:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")
                self.log_file.write(f"{timestamp}, {hex(message.arbitration_id)}, {message.data.hex()}, READ\n")
                self.log_file.flush()
                if message.arbitration_id == arbitration_id:
                    return message.data.hex()
            return None
        except Exception as e:
            print(f"OSCAROS: CAN read error - {e}")
            return None

    def send_engine_command(self, arbitration_id, data):
        """Send a command via CAN with logging."""
        if not self.can_bus:
            return False
        msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
        try:
            self.can_bus.send(msg)
            timestamp = datetime.now().strftime("%H:%M:%S.%f")
            self.log_file.write(f"{timestamp}, {hex(arbitration_id)}, {data.hex()}, WRITE\n")
            self.log_file.flush()
            print(f"OSCAROS: Sent command to ID {hex(arbitration_id)}: {data.hex()}")
            return True
        except Exception as e:
            print(f"OSCAROS: Command error - {e}")
            return False

    def send_test_command(self):
        """Send a safe test command (minimal throttle tweak)."""
        # Example: Arbitration ID 0x300, data 0x01 (minimal value, adjust based on your car)
        arbitration_id = 0x300
        data = bytearray([0x01])  # Small value to minimize risk
        success = self.send_engine_command(arbitration_id, data)
        if success:
            self.write_button.config(text="Command Sent!", state="disabled")
            self.root.after(2000, lambda: self.write_button.config(text="Send Test Throttle Command (ID 0x300)", state="normal"))

    def update_data(self):
        """Update UI with live data."""
        while self.running:
            rpm = self.read_engine_rpm()
            speed = self.read_speed()
            temp = self.read_coolant_temp()
            throttle = self.read_throttle_position()
            fuel = self.read_fuel_level()
            intake = self.read_intake_air_temp()
            can_throttle = self.read_can_sensor(0x201)  # Throttle example
            can_steering = self.read_can_sensor(0x202)  # Steering example

            self.rpm_label.config(text=f"RPM: {rpm if rpm is not None else 'N/A'}")
            self.speed_label.config(text=f"Speed: {speed if speed is not None else 'N/A'} km/h")
            self.temp_label.config(text=f"Coolant Temp: {temp if temp is not None else 'N/A'} °C")
            self.throttle_label.config(text=f"Throttle Position: {throttle if throttle is not None else 'N/A'} %")
            self.fuel_label.config(text=f"Fuel Level: {fuel if fuel is not None else 'N/A'} %")
            self.intake_label.config(text=f"Intake Air Temp: {intake if intake is not None else 'N/A'} °C")
            self.can_throttle_label.config(text=f"CAN Throttle (ID 0x201): {can_throttle if can_throttle is not None else 'N/A'}")
            self.can_steering_label.config(text=f"CAN Steering (ID 0x202): {can_steering if can_steering is not None else 'N/A'}")

            time.sleep(1)

    def run(self):
        """Start the Tkinter main loop."""
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.root.mainloop()

    def shutdown(self):
        """Clean up connections and stop the program."""
        self.running = False
        if self.can_bus:
            self.can_bus.shutdown()
            print("OSCAROS: CAN bus disconnected")
        if self.obd_connection:
            self.obd_connection.close()
            print("OSCAROS: OBD-II disconnected")
        if self.log_file:
            self.log_file.close()
            print("OSCAROS: CAN log closed")
        self.root.quit()

# Run OSCAROS
if __name__ == "__main__":
    oscaros = OSCAROS()
    oscaros.run()