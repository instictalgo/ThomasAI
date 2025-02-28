# Thomas AI Installation Guide

This guide provides detailed instructions for installing and setting up Thomas AI.

## Prerequisites

Before installing Thomas AI, ensure you have the following prerequisites:

- Python 3.12 or higher
- pip package manager
- Git (for cloning the repository)
- Access to terminal/command line

## Installation Methods

There are several ways to install Thomas AI:

### Method 1: Install from PyPI (Recommended)

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install from PyPI
pip install thomas_ai
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/thomas_ai.git
cd thomas_ai

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

### Method 3: Using the Run Wrapper Script

```bash
# Clone the repository
git clone https://github.com/yourusername/thomas_ai.git
cd thomas_ai

# Make the wrapper script executable
chmod +x run_wrapper.sh

# Run the wrapper script
./run_wrapper.sh
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to configure your installation:
   ```
   # Required configurations
   API_PORT=8002
   DASHBOARD_PORT=8003
   
   # Optional: Add your API keys for AI integration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional: Database configuration (default is SQLite)
   # DATABASE_URL=postgresql://user:password@localhost/thomas_ai
   ```

## Verifying Installation

After installation, verify that Thomas AI is working correctly:

1. Start the API server:
   ```bash
   thomas-api
   ```

2. In a separate terminal, start the dashboard:
   ```bash
   thomas-dashboard
   ```

3. Open your web browser and navigate to:
   - Dashboard: http://localhost:8003
   - API Documentation: http://localhost:8002/docs

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   
   If you see an error about ports already in use:
   ```bash
   # Check what's using the port
   sudo lsof -i :8002
   # Kill the process
   sudo kill -9 <PID>
   ```

2. **Database Errors**
   
   If you encounter database connection issues:
   ```bash
   # Reset the database
   rm thomas_ai.db
   python init_db.py
   ```

3. **Module Import Errors**
   
   For Python module import errors:
   ```bash
   # Make sure all dependencies are installed
   pip install -r requirements.txt
   ```

## Next Steps

After installation, refer to the [User Guide](user_guide.md) for information on how to use Thomas AI. 