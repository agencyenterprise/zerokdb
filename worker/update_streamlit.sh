#!/bin/sh

# Retrieve the path to Streamlit's cli.py
STREAMLIT_CLI_PATH=$(poetry run python -c "import streamlit; import os; print(os.path.join(os.path.dirname(streamlit.__file__), 'web', 'cli.py'))")
echo "Streamlit CLI Path: $STREAMLIT_CLI_PATH"

# Check if cli.py exists
if [ -f "$STREAMLIT_CLI_PATH" ]; then
    echo "cli.py exists."
else
    echo "cli.py does not exist at $STREAMLIT_CLI_PATH"
    exit 1
fi

# Display a snippet of cli.py around the target line for verification
echo "Displaying lines around the target pattern:"
grep -C 3 "if __name__ == \"__main__\":" "$STREAMLIT_CLI_PATH"

# Confirm if the target pattern exists
echo "Checking if the target pattern exists..."
if grep -F "if __name__ == \"__main__\":" "$STREAMLIT_CLI_PATH"; then
    echo "Pattern found. Proceeding with modification."
else
    echo "Pattern not found. No modifications made."
    exit 1
fi

# Modify Streamlit's cli.py by inserting the new function before the main block
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS (BSD sed)
  sed -i '' '/if __name__ == "__main__":/i\
def _main_run_clExplicit(file, is_hello=False, args=[], flag_options={}):\
    bootstrap.run(file, is_hello, args, flag_options)\
' "$STREAMLIT_CLI_PATH"
else
  # Linux (GNU sed)
  sed -i '/if __name__ == "__main__":/i\
def _main_run_clExplicit(file, is_hello=False, args=[], flag_options={}):\
    bootstrap.run(file, is_hello, args, flag_options)\
' "$STREAMLIT_CLI_PATH"
fi

# Verify Modification
echo "Verifying modification..."
if grep -F "def _main_run_clExplicit(file, is_hello=False, args=[], flag_options={}):" "$STREAMLIT_CLI_PATH"; then
    echo "Modification verified successfully."
else
    echo "Modification failed."
    exit 1
fi

echo "Modification completed successfully."
