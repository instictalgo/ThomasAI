# Thomas AI User Guide

This guide explains how to use the various features of Thomas AI Management System.

## Getting Started

After [installation](installation.md), you can access Thomas AI through two main interfaces:

1. **Web Dashboard**: A graphical interface accessible through your web browser
2. **API**: A programmatic interface for integrating with other systems

## Dashboard Interface

The dashboard provides a user-friendly way to interact with Thomas AI.

### Accessing the Dashboard

Open your web browser and navigate to `http://localhost:8003` (or the port you configured).

### Dashboard Sections

The dashboard is organized into several sections:

#### 1. Overview Dashboard

The main dashboard page provides an overview of all projects, payments, and key metrics.

- **Business Overview**: Shows key metrics like active projects, total payments, and team size
- **Projects**: Displays cards for each active project with basic information
- **Recent Payments**: Shows the most recent payments made

#### 2. Payments

The payments section allows you to:

- Create new payments to team members
- View payment history
- Filter payments by employee
- Export payment data

#### 3. Payment Details

This section provides detailed payment information for specific team members:

- Payment history for individual team members
- Payment visualizations and trends
- Total amounts paid by currency

#### 4. Projects

The projects section allows you to:

- Create new projects
- Set budgets and timelines
- Assign team members
- Track project progress

#### 5. Chat with Thomas

The AI-powered chat interface allows you to:

- Ask questions about your projects and payments
- Get insights and recommendations
- Request analyses of project data

#### 6. Assets

The assets section helps you:

- Track game development assets
- Monitor progress and dependencies
- Assign assets to team members

#### 7. System Status

The system status page provides:

- API and database status information
- Performance metrics
- Database tables information

## API Interface

Thomas AI provides a RESTful API for programmatic access.

### API Documentation

Access the API documentation at `http://localhost:8002/docs`.

### Common API Endpoints

- `GET /projects/`: List all projects
- `POST /projects/`: Create a new project
- `GET /payments/`: List all payments
- `POST /payments/`: Create a new payment
- `GET /health`: Check API health

### API Authentication

(API authentication features coming in a future release)

## Command-Line Scripts

Thomas AI includes several helpful scripts:

### Starting the System

```bash
./run_wrapper.sh
```

This script starts the API server and dashboard interface.

### Stopping the System

```bash
./stop_thomas.sh
```

This script gracefully stops all Thomas AI services.

## Advanced Features

### AI-Powered Assistance

The "Chat with Thomas" feature provides:

- Natural language interface to your data
- Project recommendations
- Payment analysis
- Budget forecasting

### Data Context Controls

When chatting with Thomas, you can select what information the AI can access:

- Project Information
- Payment Data
- Employee Information
- Asset Progress

## Troubleshooting

For common issues, refer to the [Troubleshooting](installation.md#troubleshooting) section in the installation guide. 