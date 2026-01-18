# String Search Server

A high-performance TCP string search server built in Python.  
It searches for **exact line matches** in a large text file and supports concurrent queries.

This project was developed as a complete implementation following a technical assessment specification, including unit tests, performance benchmarks, PDF report generation, and deployment as a Linux systemd service.

## Features

- Concurrent client connections using threading
- Two operating modes:
  - **Cached** (`REREAD_ON_QUERY=False`): Loads entire file into memory → extremely fast (~0.1ms/query)
  - **Reread** (`REREAD_ON_QUERY=True`): Reads file on every query → suitable for dynamic files
- Configurable via `config.ini` (host, port, file path, SSL, workers)
- Detailed DEBUG logging with timestamp, IP, query time, and result
- Unit tests (pytest)
- Performance benchmarks comparing 5 search methods
- Auto-generated PDF performance report with tables & charts
- Runs as a proper Linux systemd daemon/service

## Project Structure
string-search-server/
├── benchmarks/               ← Benchmark scripts & PDF generator
├── data/                     ← Test files (e.g. 200k.txt)
├── scripts/                  ← Helper scripts (test data generation, etc.)
├── src/                      ← Core code
│   ├── init.py
│   ├── server.py             ← Main TCP server
│   └── searcher.py           ← Search engine logic
├── tests/                    ← Unit tests
├── systemd/                  ← Service file for daemon deployment
├── client.py                 ← Simple test client
├── config.ini                ← Configuration file
├── requirements.txt          ← Dependencies
├── README.md
└── performance_report.pdf    ← Benchmark results (generated)

## Requirements

- Python 3.8+
- Linux (for systemd service)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/malechmwaniiki/string-search-server.git
   cd string-search-server
   Create and activate virtual environment:Bashpython3 -m venv venv


## Benchmark & Reports

- Run performance benchmarks:
  ```bash
    cd benchmarks
    python3 benchmark_search.py
   python3 generate_report.py

Built With

Python 3
socket, threading, mmap, configparser
pytest, matplotlib, reportlab, pandas
