
# 📦 Raremotion Inventory System

A lightweight inventory and sales management application developed by Raremotion Labs.

## Overview

Raremotion Inventory System helps small businesses manage products, monitor stock levels, record sales, and review business performance through a simple dashboard.

## Features

- Inventory dashboard
- Add, edit, and delete products
- Product categories and selling prices
- Stock In and Stock Out management
- Low-stock alerts
- Sales recording
- Automatic stock deduction after sales
- Revenue tracking
- Sales history
- Business reports and analytics
- Inventory and sales CSV exports

## Technology Stack

- Python
- Streamlit
- SQLite
- Pandas

## Installation

Clone the repository:

```bash
git clone https://github.com/RareBuilderAI/raremotion-inventory-system.git
cd raremotion-inventory-system
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
streamlit run app.py
```

## Database

The application uses SQLite for local data storage.

The database file is created automatically when the application starts.

The local database is excluded from Git to protect business records.

## Deployment Notes

SQLite stores data in a local file. On hosting services with ephemeral filesystems, inventory and sales records may disappear after restarts or redeployments.

For persistent production use, migrate the database to a managed database service and add authentication before allowing real businesses to use the application.

## Developer

**Raremotion Labs**

Building practical software solutions for modern businesses.

## Project Status

Version 1.0 — Local MVP

Core inventory and sales functionality implemented and tested locally.

## Public demo deployment

Deploy `demo.py` (not `app.py`) from this repository on Streamlit Community Cloud.
Use Python 3.14, matching the tested local environment, and the pinned requirements.
The demo starts with an empty database for each visitor. Add fictional sample
products to exercise stock changes, sales, analytics, and CSV exports.
Never upload `inventory.db`, secrets, or private business records.

The demo has no production authentication. Its per-session temporary SQLite files
are disposable and may disappear on reconnection, restart, or redeployment.
For local business use, continue to run `streamlit run app.py`; it retains the
existing local database. The demo entry point does not open that database.
