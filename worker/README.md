# Running the Worker application

## Table of Contents

- [Python Version](#python-version)
- [Installation](#installation)
- [Virtual Environment](#virtual-environment)
- [Installing Packages](#installing-packages)
- [Running the Application](#running-the-application)
- [Building the Executable](#building-the-executable)

## Python Version

This project uses **Python 3.12**. Ensure that you have the correct Python version installed on your system. You can check your Python version by running:

```bash
python --version
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/agencyenterprise/0k-platform.git
   cd 0k-platform/worker
   ```

1. **Install Poetry:**

   Poetry is a dependency management tool for Python. Install it by following the instructions [here](https://python-poetry.org/docs/#installation).

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   Or use `pip`:

   ```bash
   pip install poetry
   ```

## Virtual Environment

Poetry automatically creates and manages virtual environments. To create a virtual environment, simply run:

```bash
poetry shell
```

This will create and activate the virtual environment. If you want to deactivate it later, just run `exit`.

## Installing Packages

To install the dependencies specified in your pyproject.toml file, run:

```bash
poetry install
```

## Running the Application

```bash
python run_main.app
```

## Building the Executable

1. **Setting up pyenv:**

```
cd worker
python3 -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
```

1. **Install deps for build:**

```
pip install -r requirements.txt
```

1. **Env variables:**
   Create a `.env` file from `.env.example`

```
HUB_URL=http://localhost:8000
```

1. **Building and packaging solution:**

```
pyinstaller run_main.spec
```

1. **Running executable:**

```
./dist/run_main
```
