# Thomas AI

An AI-powered management system for game development projects.

## Overview

Thomas AI is a comprehensive tool designed to streamline game development workflows through AI-assisted project management. It provides both an API service and a dashboard interface for monitoring and managing game development projects.

## Features

- **API Service**: RESTful API for programmatic access to Thomas AI capabilities
- **Dashboard**: Interactive web interface for project monitoring and management
- **AI-Powered Analysis**: Intelligent insights for game development workflows
- **Knowledge Management**: Game design knowledge base with document processing capabilities
- **Enhanced Knowledge System**: Version-controlled, taxonomy-organized knowledge with relationship visualization

## Documentation

Comprehensive documentation is available in the [Docs](Docs/) folder:

- [Installation Guide](Docs/installation.md) - Detailed installation instructions
- [User Guide](Docs/user_guide.md) - How to use Thomas AI
- [Knowledge Management](Docs/knowledge_management.md) - Guide to the knowledge management system
- [Contributing Guidelines](Docs/CONTRIBUTING.md) - Guidelines for contributing to the project
- [Changelog](CHANGELOG.md) - Version history and changes

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
- `scripts/migrate_to_postgresql.py`: Migrate data from SQLite to PostgreSQL

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

## Knowledge Management

Thomas AI includes a comprehensive knowledge management system for game design:

### Features

- **Game Design Concepts**: Store and retrieve fundamental game design principles and mechanics
- **Industry Practices**: Document successful approaches used in the game industry
- **Educational Resources**: Catalog learning materials for game development
- **Market Research**: Track market trends and player preferences
- **Document Processing**: Extract knowledge from game design documents, research papers, and other materials
- **Taxonomy & Categorization**: Organize knowledge in hierarchical taxonomies
- **Relationships**: Create and visualize relationships between knowledge items
- **Version Control**: Track changes to knowledge items over time
- **Collaborative Editing**: Lock, edit, and review knowledge with team members
- **Visualization**: Interactive graph visualizations of knowledge relationships

### Using the Knowledge Base

1. Access the Knowledge Manager from the dashboard navigation
2. Toggle between the standard and enhanced Knowledge Manager
3. Add entries manually through the appropriate forms
4. Upload documents to automatically extract game design knowledge
5. Search the knowledge base to find relevant information for your projects
6. Visualize knowledge relationships and taxonomies

## Database Support

Thomas AI supports both SQLite and PostgreSQL databases:

- **SQLite**: Default for simple deployments and development
- **PostgreSQL**: For production environments with increased scalability and concurrency

To use PostgreSQL, set the `DATABASE_URL` environment variable:

```bash
# Example PostgreSQL connection string
export DATABASE_URL="postgresql://username:password@localhost:5432/thomas_ai"
```

A migration script is provided to transfer data from SQLite to PostgreSQL:

```bash
python scripts/migrate_to_postgresql.py --sqlite-path path/to/sqlite.db --pg-connection postgresql://user:pass@host:port/dbname
```

## Version History

- **1.07** - Current development version: Enhanced knowledge management system with taxonomy and visualization
- **1.06** - Knowledge Management System
- **1.05** - Documentation reorganized, GitHub structure updated
- **1.0.0** - Initial release: Core functionality, API and dashboard interfaces

## License

[MIT License](LICENSE)

## Contact

For questions or support, please contact: your-email@example.com 