# Python Sandbox

A personal sandbox for learning and experimenting with Python. Projects will be added over time as new lessons are completed.

## Projects

### Lesson 1 — Simple Filter

A small command-line program that reads a JSON file of people and lets you filter the list by age, name, and/or city.

- **Location:** `simple_filter/`
- **Data file:** `simple_filter/people.json`
- **Entry point:** `simple_filter/main.py`

You can combine filters. Name and city matches are case-insensitive. Age uses a signed number:

| Age input | Meaning |
| --- | --- |
| Positive number (for example `40`) | People whose age is **greater than or equal to** that number |
| Negative number (for example `-30`) | People whose age is **less than or equal to** the absolute value |
| Blank | Do not filter by age |

At least one of age, name, or city must be provided. After each search you can run another query or exit.

### Lesson 2 — Log Parser

A command-line program that reads a log file, skips malformed lines, and prints a summary of the valid entries.

- **Location:** `log_parser/`
- **Sample data:** `log_parser/sample.log`
- **Entry point:** `log_parser/main.py`

Each valid line must look like:

```text
YYYY-MM-DD HH:MM:SS LEVEL message
```

Allowed levels are `INFO`, `DEBUG`, `WARNING`, `ERROR`, and `CRITICAL`. Anything that does not match is counted as skipped.

The summary includes:

- First and last timestamps
- Counts of valid and skipped lines
- Counts per log level
- The five most common messages

You can print the report to the terminal and optionally write it to a `.txt` or `.json` file.

## Requirements

- [Python 3.12+](https://www.python.org/downloads/) (3.13 is what this repo was developed with)
- A terminal (Command Prompt, PowerShell, or Git Bash on Windows)

Both apps use only the Python standard library. Tests use [pytest](https://pytest.org/) and [pytest-cov](https://pytest-cov.readthedocs.io/). Optional task shortcuts use [Poe the Poet](https://poethepoet.github.io/poethepoet/).

## Getting started

Clone the repository and create a virtual environment from the project root:

```bash
git clone https://github.com/scottycompton/python_sandbox.git
cd python_sandbox
python -m venv .venv
```

Activate the virtual environment:

```bash
# Git Bash / macOS / Linux
source .venv/Scripts/activate   # Windows Git Bash
# source .venv/bin/activate     # macOS / Linux

# PowerShell
.venv\Scripts\Activate.ps1

# Command Prompt
.venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install -r requirements.txt
```

That installs pytest, pytest-cov, and poethepoet. Add new packages to `requirements.txt` as later lessons need them.

## Running Simple Filter

Run the program from the project root so it can find `simple_filter/people.json`:

```bash
python simple_filter/main.py
# or: poe run-simple-filter
```

You will be prompted for age, name, and city. Leave a field blank to skip that filter. After results are shown, press **Enter** to search again or type **X** to exit.

Example session:

```text
Age:  40
Name:
City: Chicago
```

That search returns people who are at least 40 and live in Chicago.

## Running Log Parser

Run the program from the project root. `--log` / `-l` is required. `--out` / `-o` is optional and must end in `.txt` or `.json`.

```bash
python log_parser/main.py -l log_parser/sample.log
python log_parser/main.py -l log_parser/sample.log -o report.txt
python log_parser/main.py -l log_parser/sample.log -o report.json
```

From inside `log_parser/`, the sample file is just `sample.log`:

```bash
cd log_parser
python main.py -l sample.log
python main.py -l sample.log -o report.txt
```

Errors (missing file, permission denied, no valid lines, or an unsupported output suffix) are printed to stderr.

## Running tests

From the project root, with the virtual environment activated:

```bash
pytest
poe test-simple-filter
poe test-simple-filter-cov
poe test-log-parser
poe test-log-parser-cov
```

`pytest` runs every test. The `poe test-*` tasks run one project at a time. The `*-cov` tasks also print a coverage report with missing lines.

## Project structure

```text
python_sandbox/
├── README.md
├── pyproject.toml       # pytest config and poe task shortcuts
├── requirements.txt
├── .gitignore
├── simple_filter/
│   ├── main.py          # Filter app
│   ├── people.json      # Sample people data
│   └── test_main.py     # pytest coverage of the filter functions
└── log_parser/
    ├── main.py          # Log parser app
    ├── sample.log       # Sample log file (valid lines mixed with garbage)
    └── test_main.py     # pytest coverage of the parser and report functions
```

## Adding a new project

When you add another lesson:

1. Put it in its own folder (`simple_filter/`, `log_parser/`, `another_project/`, and so on).
2. Add a new heading under **Projects** with a short description, location, and how to run it.
3. Update **Project structure**.
4. Add any new packages to `requirements.txt` and mention them under **Requirements** if they are not already listed.
5. Add matching `poe` tasks in `pyproject.toml` if you want shortcuts from the project root.

## License

This is a personal learning sandbox. Use and modify it as you like.
