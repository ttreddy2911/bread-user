# Project Reflection: Calculation BREAD Application

## Overview
This project involved developing a full-stack, secure calculation management system using **FastAPI** and **Vanilla JavaScript**. The core functionality follows the **BREAD** (Browse, Read, Edit, Add, Delete) pattern, with the addition of a new **Usage Statistics/Report** feature.

## Key Experiences & Challenges

### 1. Architectural Transition
Transitioning from a simple single-file FastAPI script to a structured submodule architecture (`app/`) was a significant step. This improved maintainability and allowed for cleaner separation between database models, business logic (math operations), and security utilities.

### 2. JWT Security Implementation
Implementing **OAuth2 with Password Bearer** and **JWT (JSON Web Tokens)** provided a robust security layer. The biggest challenge was ensuring that all BREAD operations were strictly scoped to the authenticated user. This was achieved by filtering database queries using the `owner_id` derived from the decoded JWT token.

### 3. Resolving the Bcrypt Compatibility Bug
A major technical hurdle was an "Internal Server Error" caused by a silent incompatibility between `passlib 1.7.4` and `bcrypt 4.x`. Since `passlib` expected a `__about__` attribute that was removed in newer `bcrypt` versions, the application would crash during password hashing. This was solved by:
1. Pinning `bcrypt==4.0.1`.
2. Implementing a **monkey-patch** in `security.py` to recreate the missing attribute, ensuring `passlib` could correctly identify the library version.

### 4. Database Schema Evolution
During development, the User model was extended to include `email` and `hashed_password`. A common issue faced was the `sqlite3.OperationalError: no such column: users.email`, which occurred because the existing database file wasn't automatically updated with new columns. The solution was to clear the old database file, allowing SQLAlchemy's `create_all()` to rebuild the schema from scratch.

### 5. New Feature: Usage Statistics Report
The added **Statistics Report** feature provides real-time insights into user activity. It aggregates total calculations, calculates average results, and identifies the most frequently used operation. This required adding a new API endpoint `/api/reports/stats` and extending the frontend UI with a "Usage Insights" card.

## Testing & Quality Assurance
The project maintains high reliability through **18 comprehensive tests** covering:
- **Unit Logic**: Verifying math operations (including edge cases like divide by zero).
- **Integration**: Ensuring routes correctly interact with the SQLite database.
- **E2E (Playwright)**: Validating the entire user journey from registration and login to performing calculations and viewing statistics.

## Conclusion
This assignment demonstrated the integration of modern web technologies, DevOps principles (CI/CD via GitHub Actions), and containerization (Docker) to deliver a professional-grade REST application.
