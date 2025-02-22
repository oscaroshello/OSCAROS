# OSCAROS - Open Source Car Operating System

Welcome to OSCAROS, an open-source framework for connecting car components and computers into a unified system. This project aims to provide a modular, extensible platform for automotive enthusiasts, developers, and researchers to experiment with car diagnostics, engine control, and future self-driving capabilities.

**Status**: Experimental / Proof-of-Concept  
**Warning**: OSCAROS is not certified for public road use. Use it in controlled environments (e.g., simulators, private property) at your own risk.

## Features
- **Diagnostics**: Read car data like RPM and trouble codes via OBD-II.
- **Engine Control**: Basic CAN bus commands for engine components (experimental).
- **Modular Design**: Easily add support for new car parts or protocols.

## Getting Started
1. **Prerequisites**:
   - Python 3.8+
   - CAN adapter (e.g., CANable, PiCAN) or simulator
   - OBD-II adapter (e.g., ELM327)
2. **Installation**: See [INSTALL.md](docs/INSTALL.md) for detailed steps.
3. **Run**: `python src/oscaros.py`

## Contributing
We welcome contributions! Check out [CONTRIBUTING.md](CONTRIBUTING.md) to get involved.

## License
OSCAROS is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Disclaimer
This is a research project. It’s not intended for production use or public roads without proper testing and certification. Use responsibly.

## Contact
Questions? Ideas? Open an issue or reach out on [GitHub Discussions](https://github.com/oscaroshello/OSCAROS/discussions).