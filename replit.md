# Mobile Shop Management System

## Overview

This is a desktop application for managing mobile phone shops, built using PyQt6 with comprehensive Arabic RTL (Right-to-Left) support. The system provides a complete management solution for mobile phone retailers, handling inventory management, point-of-sale operations, repairs tracking, digital wallet transactions, and comprehensive reporting. The application features a modern, beautiful UI with animations and follows Arabic language conventions throughout the interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: PyQt6 for desktop application development
- **Language Support**: Full Arabic RTL layout with proper text rendering
- **UI Pattern**: Modern desktop application with sidebar navigation and stacked content pages
- **Animation System**: Custom animated widgets and transitions using QPropertyAnimation
- **Styling**: Centralized modern styling system with consistent color palette and typography
- **Component Structure**: Modular page-based architecture with reusable UI components and dialogs

### Backend Architecture
- **Database Layer**: SQLite with enhanced configuration for UTF-8 support and performance optimization
- **Data Access Pattern**: Centralized DatabaseManager class handling all database operations
- **Business Logic**: Service layer integrated within UI components for desktop application simplicity
- **Error Handling**: Comprehensive logging system with database operation tracking
- **Threading**: Background database operations to prevent UI blocking

### Application Structure
- **Main Entry Point**: `main.py` with application initialization and splash screen
- **Window Management**: Single main window with tabbed/stacked page navigation
- **Page Components**: Separate modules for Dashboard, Inventory, Sales/POS, Repairs, Wallet, and Reports
- **UI Components**: Reusable widgets, dialogs, and styling in dedicated UI modules
- **Database Utilities**: Centralized database management with connection pooling and error recovery

### Data Management
- **Local Storage**: SQLite database for all application data with Arabic text support
- **Database Schema**: Comprehensive schema covering products, sales, repairs, transactions, customers, and analytics
- **Data Validation**: Input validation and sanitization at both UI and database levels
- **Backup Strategy**: Database backup functionality with recovery mechanisms
- **Performance**: Optimized queries with proper indexing and connection management

## External Dependencies

### Core Framework
- **PyQt6**: Primary GUI framework for desktop application development
- **SQLite3**: Embedded database engine (built into Python standard library)

### Python Standard Library
- **logging**: Application logging and error tracking
- **datetime**: Date/time handling for transactions and reporting
- **uuid**: Unique identifier generation for records
- **csv/json**: Data import/export functionality
- **os/shutil**: File system operations for database backup

### Development Dependencies
- **typing**: Type hints for better code maintainability
- **calendar**: Calendar operations for reporting features

### Optional Integrations
- **File System**: Local file operations for data export, import, and backup
- **Print Services**: System print dialogs for invoices and reports (through PyQt6)

The application is designed as a standalone desktop solution with minimal external dependencies, focusing on reliability and offline operation capabilities for mobile shop environments.