import os
import sys
import inspect
from streamlit.web import cli as stcli

def run_streamlit():
    app_source_code = inspect.getsource(sys.modules['main'])

    with open('.main.py', 'w') as f:
        f.write(app_source_code)

    os.makedirs('.streamlit', exist_ok=True)

    with open('.streamlit/config.toml', 'w') as f:
        f.write("""
[global]
developmentMode = false

[server]
port = 8502
        """)

    stcli._main_run_clExplicit('.main.py', args=['--run'], flag_options={
        "server.enableCORS": True,
        "server.enableXsrfProtection": False,
    })

if __name__ == '__main__':
    import main

    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # Run in CLI mode
        wallet = os.environ.get('WALLET_ADDRESS')
        api_key = os.environ.get('PINATA_API_KEY')
        if not wallet or not api_key:
            print("Error: Both WALLET_ADDRESS and PINATA_API_KEY environment variables are required for CLI mode.")
            sys.exit(1)
        main.run_cli(wallet, api_key)
    else:
        # Run in Streamlit mode
        print("Running in Streamlit mode")
        run_streamlit()
