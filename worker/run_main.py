import os
import main
import inspect
from streamlit.web import cli


if __name__ == '__main__':
    app_source_code = inspect.getsource(main)

    with open('.main.py', 'w') as f:
        f.write(app_source_code)

    os.makedirs('.streamlit', exist_ok=True)

    with open('.streamlit/config.toml', 'w') as f:
        f.write("""
[global]
developmentMode = false

[server]
headless = true
port = 8502
address = "0.0.0.0"
                """)

    cli._main_run_clExplicit('.main.py', args=['run'],flag_options={
        "server.enableCORS": True,
        "server.enableXsrfProtection": False,
        "server.port": 8502,
        "server.address": "0.0.0.0"
    })
