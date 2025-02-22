# Installation Guide for OSCAROS

Follow these steps to set up OSCAROS on your system.

## Prerequisites
- **OS**: Linux (Ubuntu recommended) or Windows/Mac with adjustments.
- **Python**: 3.8 or higher.
- **Hardware** (optional):
  - CAN adapter (e.g., CANable, PiCAN).
  - OBD-II adapter (e.g., ELM327 Bluetooth/USB).
- **Simulator** (optional): Linux `vcan0` for testing without hardware.

## Steps
1. **Install Python**:
   - Linux: `sudo apt update && sudo apt install python3 python3-pip`
   - Windows/Mac: Download from [python.org](https://www.python.org).

2. **Clone the Repo**:
   ```bash
   git clone https://github.com/oscaroshello/OSCAROS.git
   cd OSCAROS