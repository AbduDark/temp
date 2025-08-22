# Mobile Shop Management System

## Overview

This is a comprehensive desktop application for managing a mobile shop built with Python and PySide6. The system provides a complete POS (Point of Sale) solution with inventory management, repair tracking, customer management, reporting, and daily operations management. The application is designed to work offline with a local SQLite database and features a modern Arabic-language interface optimized for Windows desktop environments.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **UI Framework**: PySide6 (Qt for Python) for modern desktop interface
- **Layout Direction**: Right-to-left (RTL) for Arabic language support
- **Window Management**: Modular window system with main window containing stacked widgets
- **Components**:
  - Main Window with dashboard and navigation
  - Specialized windows for POS, inventory, repairs, reports, settings
  - Modal dialogs for data entry and editing
  - Custom widgets for dashboard metrics and forms

### Backend Architecture
- **Language**: Python 3.x with object-oriented design
- **Service Layer**: Separated business logic into service classes
  - AuthService for authentication and user management
  - POSService for sales transactions
  - InventoryService for stock management
  - RepairService for repair ticket management
  - ReportService for analytics and reporting
  - BackupService for data backup/restore
- **Model Layer**: Database abstraction with dedicated model classes
  - DatabaseManager for connection handling
  - Model classes for User, Product, Sale, Repair entities

### Data Storage Solutions
- **Database**: SQLite local database (`data/shop.db`)
- **Schema Design**: Normalized relational structure with foreign key constraints
- **Tables**: users, products, categories, sales, sale_items, customers, repair_tickets, settings
- **Backup Strategy**: ZIP-based backup system including database and reports

### Authentication and Authorization
- **Password Security**: bcrypt hashing for user passwords
- **Role-based Access**: Admin, Manager, Cashier, Technician roles
- **Session Management**: In-memory user session tracking
- **Permissions**: Granular permission system for different operations

### Key Features
- **Multi-language Support**: Arabic interface with RTL layout
- **POS System**: Complete sales workflow with multiple payment methods
- **Inventory Management**: Stock tracking with low-stock alerts
- **Repair Management**: Ticket-based repair workflow
- **Reporting**: Sales, inventory, and repair analytics
- **Daily Operations**: Daily closing procedures with cash reconciliation

## External Dependencies

### Core Framework
- **PySide6**: Qt-based GUI framework for desktop interface
- **SQLite3**: Built-in Python database engine (no external server required)

### Data Processing
- **bcrypt**: Password hashing and authentication security
- **pathlib**: Modern path handling (Python standard library)
- **datetime**: Date and time operations (Python standard library)
- **json/csv**: Data export formats (Python standard library)

### PDF Generation
- **ReportLab**: PDF generation for invoices and reports (optional dependency)
- **Alternative**: Built-in HTML-to-PDF conversion if ReportLab unavailable

### Deployment
- **PyInstaller**: Converting Python application to Windows executable
- **Assets Management**: Local icon and font storage in `assets/` directory

### File System Dependencies
- **Directory Structure**: 
  - `data/` - Database storage
  - `assets/icons/` - Application icons
  - `reports/` - Generated reports
  - `backup/` - Database backups
  - `logs/` - Application logs

### Optional Integrations
- **Arabic Font Support**: NotoSansArabic-Regular.ttf for proper Arabic rendering
- **Barcode Generation**: For product barcoding (implementation ready)
- **Printer Support**: Direct printing capabilities through Qt print system