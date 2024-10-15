import sys
import os
import base64
import threading
import queue
import time
from dotenv import load_dotenv
from Crypto.PublicKey import RSA
import schedule
import streamlit as st

from services.registration_service import register
from jobs.process_designated_proof_requests import process_designated_proof_requests

# Load environment variables
load_dotenv()

# Global variables
log_queue = queue.Queue()
worker_running_event = threading.Event()  # Event to safely control the worker state

# Custom Logger to Redirect Print Output
class StreamlitLogger:
    def write(self, message):
        if message.strip():  # Avoid blank lines
            log_queue.put(message.strip())

    def flush(self):
        pass  # No need to implement flush for our use case

def start_worker(pina_api_key, wallet):
    """Start the worker and scheduling."""
    global auth_public_key, auth_private_key
    print("Starting worker...")

    # Generate RSA keys
    key = RSA.generate(2048)
    auth_private_key = key.export_key()
    auth_public_key = key.publickey().export_key()

    print(f"Worker public key: {base64.b64encode(auth_public_key).decode()}")

    # Register worker
    print('Worker registration initiated...')
    signature_message_id, worker_id, signature = register(auth_public_key, auth_private_key, wallet)
    print(f'Worker {worker_id} registered successfully.')

    # Schedule jobs
    print("Starting jobs...")
    schedule.every(5).seconds.do(process_designated_proof_requests, signature_message_id, signature, pina_api_key)

def stop_worker():
    """Stop the worker and clear the scheduled jobs."""
    print("Stopping worker...")
    if 'st' in globals():
        st.session_state.worker_running = False
        st.session_state.log_messages = []

    schedule.clear()
    worker_running_event.clear()
    print("Jobs stopped.")
    if 'st' in globals():
        st.rerun()

def run_schedule():
    """Run pending scheduled jobs."""
    schedule.run_pending()

def run_streamlit():
    st.title("ZerokDB Worker Setup")
    st.subheader("Welcome to the ZerokDB Worker!")
    st.markdown('<br style="margin-bottom:16px">', unsafe_allow_html=True)

    # Initialize session state
    if 'worker_running' not in st.session_state:
        st.session_state.worker_running = False

    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []  # Initialize log messages in session state

    # Create two columns layout
    col1, _, col2 = st.columns([1, 0.1, 1])

    # Right Column: Application Logs
    with col2:
        st.write("Application Logs")
        st.markdown(
            """
            <style>
            .custom-log-area {
                margin-top: -16px;
                background-color: rgb(180, 180, 180);
                border-radius: 8px;
                padding: 10px;
                height: 310px;
                width: 360px;
                overflow-y: auto;
                color: var(--text-color);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        log_area_placeholder = st.empty()

    # Left Column: Input and Button
    with col1:
        st.markdown('<div style="padding: 0px 0px 10px 0px">Start the worker to start earning rewards for verifying proofs.</div>', unsafe_allow_html=True)

        wallet_address = st.text_input("Enter your APTOS wallet address")
        pinata_api_key = st.text_input("Enter your Pinata API Key", type='password')
        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

        # Button Area
        button_area = st.empty()  # Create a placeholder for the button

        if not st.session_state.worker_running:
            # Start Worker Button
            if button_area.button("Start Worker"):
                if wallet_address and pinata_api_key:
                    st.session_state.worker_running = True
                    print(f"Using wallet address: {wallet_address}")
                    start_worker(pinata_api_key, wallet_address)
                else:
                    print("Please enter a valid wallet address and Pinata API Key!!!")
        else:
            # Stop Worker Button
            if button_area.button("Stop Worker"):
                stop_worker()

    # Display Logs
    log_area_placeholder.markdown(
        f"<div class='custom-log-area'>{'<br>'.join(st.session_state.log_messages)}</div>",
        unsafe_allow_html=True
    )

    # Run the schedule if the worker is running
    if st.session_state.worker_running:
        run_schedule()

    # Continuously Display Logs from the Queue without excessive refreshes
    if st.session_state.worker_running:
        while not log_queue.empty():
            log_message = log_queue.get()
            st.session_state.log_messages.append(log_message)  # Store log message in session state
        time.sleep(2)  # Sleep to reduce the frequency of updates
        st.rerun()

def run_cli(wallet, api_key):
    print(f"Starting worker in CLI mode with wallet: {wallet}")
    start_worker(api_key, wallet)

    while True:
        run_schedule()
        time.sleep(2) # Sleep to reduce the frequency of updates

def main():
    sys.stdout = StreamlitLogger()  # Redirect stdout to the custom logger
    cli = os.environ.get('CLI')
    if cli:
        wallet = os.environ.get('WALLET_ADDRESS')
        api_key = os.environ.get('PINATA_API_KEY')
        if not wallet or not api_key:
            print("Error: Both wallet address and API key are required for CLI mode.")
            sys.exit(1)
        run_cli(wallet, api_key)
    else:
        run_streamlit()

if __name__ == "__main__":
    main()
