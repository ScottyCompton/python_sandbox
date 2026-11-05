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

## Requirements

- [Python 3.12+](https://www.python.org/downloads/) (3.13 is what this repo was developed with)
- A terminal (Command Prompt, PowerShell, or Git Bash on Windows)

The Simple Filter app uses only the Python standard library. Tests use [pytest](https://pytest.org/).

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

Right now that only installs [pytest](https://pytest.org/) for running tests. Add new packages to `requirements.txt` as later lessons need them.

## Running Simple Filter

Run the program from the `simple_filter` directory so it can find `people.json`:

```bash
cd simple_filter
python main.py
```

You will be prompted for age, name, and city. Leave a field blank to skip that filter. After results are shown, press **Enter** to search again or type **X** to exit.

Example session:

```text
Age:  40
Name:
City: Chicago
```

That search returns people who are at least 40 and live in Chicago.

## Running tests

From the `simple_filter` directory, with the virtual environment activated and pytest installed:

```bash
cd simple_filter
pytest test_main.py
```

## Project structure

```text
python_sandbox/
├── README.md
├── requirements.txt
├── .gitignore
└── simple_filter/
    ├── main.py          # Filter app
    ├── people.json      # Sample people data
    └── test_main.py     # pytest coverage of the filter functions
```

## Adding a new project

When you add another lesson:

1. Put it in its own folder (`simple_filter/`, `another_project/`, and so on).
2. Add a new heading under **Projects** with a short description, location, and how to run it.
3. Update **Project structure**.
4. Add any new packages to `requirements.txt` and mention them under **Requirements** if they are not already listed.

## License

This is a personal learning sandbox. Use and modify it as you like.
