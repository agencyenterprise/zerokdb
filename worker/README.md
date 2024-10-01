# Running the Worker application

## Table of Contents

- [Python Version](#python-version)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Create a Virtual Environment](#create-a-virtual-environment)
  - [Install Dependencies](#install-dependencies)
  - [Environment Variables](#environment-variables)
  - [Modifying Streamlit Library](#modifying-streamlit-library)
- [Running the Application](#running-the-application)
- [Building the Executable](#building-the-executable)

## Python Version

This project uses **Python 3.12**. Ensure that you have the correct Python version installed on your system. You can check your Python version by running:

```bash
python --version
```

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/agencyenterprise/zerokdb.git
   cd zerokdb/worker
   ```

1. **Create a Virtual Environment**

   it's advisible to have a venv only for the worker to run adn build it run:

   ```bash
   python3.12 -m venv venv
   ```

   and:

   ```bash
   source venv/bin/activate # On Windows use `venv\Scripts\activate`
   ```

   This will create and activate the virtual environment. If you want to deactivate it later, just run `deactivate`.

1. **Install Dependencies**

   Poetry automatically creates and manages virtual environments. To create a virtual environment, simply run:

   ```bash
   pip install -r requirements.txt
   ```

   This will create and activate the virtual environment. If you want to deactivate it later, just run `deactivate`.

1. **Environment Variables**
   Create a `.env` file from `.env.example`

   ```bash
   HUB_URL=http://localhost:8000
   ```

1. **Modifying Streamlit Library**

   Unfortunatelly for building a python executable with Streamlit we need to alter some code in the lib itself, copy this code:

   ```bash
   def _main_run_clExplicit(file, is_hello=False, args=[], flag_options={}):
      bootstrap.run(file, is_hello, args, flag_options)
   ```

   And past it on the `cli.py` file anywhere before the main function on it, this file is located at `venv/lib/python3.12/site-packages/streamlit/web/cli.py`

## Running the Application

```bash
python run_main.py
```

## Building the Executable

1. **Building and packaging solution:**

   ```bash
   pyinstaller run_main.spec
   ```

1. **Running executable:**

   ```bash
   ./dist/run_main
   ```
