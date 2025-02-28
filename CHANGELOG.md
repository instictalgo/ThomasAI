# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.07] - Unreleased

### Added

- Enhanced knowledge management system with:
  - Version control and revision history for knowledge entries
  - Taxonomy and hierarchical organization of knowledge
  - Visualization of knowledge relationships
  - Collaborative editing with locking and review workflows
  - Advanced search capabilities (keyword + semantic search)
  - Improved caching for better performance
- Knowledge graph visualization component 
- PostgreSQL support for improved scalability and concurrent access
- Migration script to help transfer data from SQLite to PostgreSQL

### Changed

- Refactored knowledge base implementation to use SQLAlchemy models
- Enhanced API with new endpoints for knowledge management
- Updated dashboard UI to include enhanced knowledge manager
- Added toggle to switch between new and legacy knowledge manager UIs

### Fixed

- Improved error handling in API and database connections
- Fixed caching issues in knowledge base queries

## [1.06] - 2023-05-15

### Added

- Knowledge Management System for game design knowledge
- Document processing capabilities
- Integration with OpenAI for knowledge extraction
- New UI components for knowledge management

### Fixed

- Bug fixes and performance improvements

## [1.05] - 2023-05-01

- Documentation reorganized
- GitHub structure updated
- Various bug fixes and improvements

## [1.0.0] - 2023-04-15

- Initial release
- Core functionality implemented
- Basic API and dashboard interfaces 