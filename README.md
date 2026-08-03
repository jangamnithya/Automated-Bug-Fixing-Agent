# Automated Bug-Fixing Agent

An intelligent Python-based framework that automates test execution, detects software failures, and generates structured bug reports as a foundation for automated bug localization and AI-assisted code repair.

**Status:** Active Development

---

# Overview

Debugging is one of the most time-consuming phases of software development. This project aims to automate the initial stages of debugging by executing test suites, collecting failure information, and preparing structured data for future automated bug analysis and repair.

The project is being developed incrementally with a strong emphasis on clean architecture, modular design, and maintainable code.

---

# Objectives

The primary objectives of this project are:

- Automate test execution
- Detect failing tests
- Generate structured bug reports
- Extract stack trace information
- Build the foundation for automated bug localization
- Enable future AI-assisted bug repair

---

# Features Implemented

- Modular project architecture using the `src` layout
- Automated test execution with `pytest`
- Detection of total, passed, and failed tests
- Collection of failed test information
- Structured bug reports using Pydantic models
- Initial Stack Trace Parser implementation
- Git version control and GitHub integration

---

# Project Structure

```text
bug-fixing-agent/
│
├── sample_project/
│   ├── calculator.py
│   └── test_calculator.py
│
├── src/
│   ├── agent/
│   ├── models/
│   │   └── bug_report.py
│   ├── parser/
│   │   ├── python_parser.py
│   │   └── stack_trace_parser.py
│   ├── runner/
│   │   └── test_runner.py
│   ├── utils/
│   └── main.py
│
├── .gitignore
└── README.md
```

---

# Architecture

```text
                  Sample Project
                         │
                         ▼
                  Test Runner
                         │
                         ▼
                 Bug Report Model
                         │
                         ▼
                Stack Trace Parser
                         │
                         ▼
          Future Bug Localization Engine
                         │
                         ▼
            Future AI Repair Engine
```

---

# Workflow

```text
Execute Test Suite
        │
        ▼
Collect Test Results
        │
        ▼
Identify Failed Tests
        │
        ▼
Generate Structured Bug Report
        │
        ▼
Extract Stack Trace Information
        │
        ▼
Prepare Data for Future Repair
```

---

# Technologies

- Python
- Pytest
- Pydantic
- Regular Expressions
- Git
- GitHub

---

# Installation

Clone the repository:

```bash
git clone https://github.com/jangamnithya/bug-fixing-agent.git
cd bug-fixing-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install pytest pydantic
```

Run the project:

```bash
python -m src.main
```

---

# Example Output

```text
========== Bug Fixing Agent ==========

Running tests...

===== Bug Report =====

Total Tests : 1
Passed      : 0
Failed      : 1

Failed Test Details

Test Name : test_add
Error     : assert -1 == 5
```

---

# Development Roadmap

## Milestone 1

Completed:

- Project setup
- Modular architecture
- Bug report models
- Test runner
- Failure detection
- Failure collection
- Initial Stack Trace Parser

Upcoming:

- Enhanced stack trace parsing
- Python AST parser
- Candidate bug localization
- Root cause ranking
- Automated validation
- Unit testing
- Integration testing
- AI-assisted repair

---

# Design Principles

The project follows the following engineering principles:

- Modular architecture
- Separation of concerns
- Extensible component design
- Structured data models
- Incremental development
- Production-oriented coding practices

---

# Current Status

The project is under active development.

Current focus areas include:

- Improving stack trace parsing
- Building Python source analysis
- Implementing automated bug localization
- Preparing the architecture for AI-assisted repair

---

# Future Vision

The long-term objective is to build an autonomous bug-fixing system capable of:

1. Executing project test suites
2. Detecting software failures
3. Identifying the root cause of defects
4. Generating repair candidates
5. Validating fixes automatically
6. Producing reliable software patches

---

# Contributing

This project is currently being developed as a personal learning and portfolio project. Feedback and suggestions are welcome.

---

# License

This project is licensed under the MIT License.