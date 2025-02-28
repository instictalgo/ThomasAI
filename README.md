# Thomas AI

An AI-powered management system for game development projects.

## Overview

Thomas AI is a comprehensive tool designed to streamline game development workflows through AI-assisted project management. It provides both an API service and a dashboard interface for monitoring and managing game development projects.

## Features

- **API Service**: RESTful API for programmatic access to Thomas AI capabilities
- **Dashboard**: Interactive web interface for project monitoring and management
- **AI-Powered Analysis**: Intelligent insights for game development workflows

## Documentation

Comprehensive documentation is available in the [Docs](Docs/) folder:

- [Installation Guide](Docs/installation.md) - Detailed installation instructions
- [User Guide](Docs/user_guide.md) - How to use Thomas AI
- [Contributing Guidelines](Docs/CONTRIBUTING.md) - Guidelines for contributing to the project

## Quick Start

### Installation

```bash
# Install from PyPI
pip install thomas_ai

# Or install from source
git clone https://github.com/yourusername/thomas_ai.git
cd thomas_ai
pip install -e .
```

### Starting the API Server

```bash
thomas-api
```

This will start the FastAPI server on the default port.

### Launching the Dashboard

```bash
thomas-dashboard
```

This will start the Streamlit dashboard interface.

### Using the Scripts

The repository includes helpful scripts for common operations:

- `run_wrapper.sh`: Start all Thomas AI services
- `stop_thomas.sh`: Stop all running Thomas AI services

## Development

### Setting Up a Development Environment

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
pytest
```

## Version History

- **1.05** - Current release: Documentation reorganized, GitHub structure updated
- **1.0.0** - Initial release: Core functionality, API and dashboard interfaces

## License

[MIT License](LICENSE)

## Contact

For questions or support, please contact: your-email@example.com 