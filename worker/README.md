# Running the Worker application

## Table of Contents

- [Running the Worker application](#running-the-worker-application)
  - [Table of Contents](#table-of-contents)
  - [Python Version](#python-version)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
  - [Building the Executable](#building-the-executable)
    - [Building the Docker Image](#building-the-docker-image)
    - [Running in Streamlit Mode](#running-in-streamlit-mode)
    - [Running in CLI Mode](#running-in-cli-mode)
    - [Environment Variables](#environment-variables)
    - [Ports](#ports)

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
   poetry install
   ```

   This will create and activate the virtual environment. If you want to deactivate it later, just run `deactivate`.

1. **Environment Variables**
   Create a `.env` file from `.env.example`

   ```bash
   HUB_URL=http://localhost:8000
   API_HOST=http://localhost:8001
   ```

1. **Modifying Streamlit Library**

   Unfortunatelly for building a python executable with Streamlit we need to alter some code in the lib itself, copy this code:

   ```bash
   def _main_run_clExplicit(file, is_hello=False, args=[], flag_options={}):
      bootstrap.run(file, is_hello, args, flag_options)
   ```

   And paste it on the `cli.py` file anywhere before the main function on it, this file is located at `venv/lib/python3.12/site-packages/streamlit/web/cli.py`

   or run

   ```bash
   sh update_streamlit.sh
   ```

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

### Building the Docker Image

First, build the Docker image:

```bash
docker build -t zerokdb-worker .
```

### Running in Streamlit Mode

To run the worker in Streamlit mode (default):

```bash
docker run -p 8502:8502 zerokdb-worker
```

This will start the Streamlit interface, accessible at `http://localhost:8502`.

### Running in CLI Mode

To run the worker in CLI mode:

```bash
docker run -e WALLET_ADDRESS=your_wallet_address -e PINATA_API_KEY=your_api_key zerokdb-worker
```

Replace `your_wallet_address` with your actual APTOS wallet address and `your_api_key` with your Pinata API key.

### Environment Variables

The following environment variables can be set:

- `WALLET_ADDRESS`: Your APTOS wallet address (required for CLI mode)
- `PINATA_API_KEY`: Your Pinata API key (required for CLI mode)
- `HUB_URL`: URL of the hub (default: http://localhost:8000)
- `API_HOST`: API host URL (default: http://localhost:8001)

You can override these variables when running the Docker container:

```bash
docker run -e HUB_URL=http://custom-hub-url -e API_HOST=http://custom-api-host zerokdb-worker
```

### Ports

The Streamlit interface runs on port 8502. Make sure to map this port when running in Streamlit mode:

```bash
docker run -p 8502:8502 zerokdb-worker
```

This setup allows for flexible deployment of the worker in both interactive (Streamlit) and automated (CLI) modes.
