import streamlit as st
import numpy as np
import base64
import matplotlib.pyplot as plt

# Local imports
from bb84 import (
    generate_random_bits, generate_random_bases, encode_qubits, 
    measure_qubits, compare_bases, check_eavesdropping, 
    extract_key, derive_key
)
from encryption import encrypt_message, decrypt_message

# We wrap the Qiskit import in a try-except block
try:
    from qiskit_viz import draw_bb84_circuit_sample
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


st.set_page_config(page_title="Quantum Secure Chat", layout="wide")

st.title("Quantum Secure Chat Application")
st.markdown("Simulate Continuous Quantum Key Distribution (CQKD) using the BB84 protocol. The system generates a brand new quantum key for every single message!")

# --- Session State Initialization ---
if 'qkd_completed' not in st.session_state:
    st.session_state.qkd_completed = False
if 'shared_key' not in st.session_state:
    st.session_state.shared_key = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'eve_detected' not in st.session_state:
    st.session_state.eve_detected = False

def run_bb84(num_bits, eve_present, noise_rate):
    """Helper function to run BB84 protocol and return the derived key or None if Eve detected."""
    alice_bits = generate_random_bits(num_bits)
    alice_bases = generate_random_bases(num_bits)
    bob_bases = generate_random_bases(num_bits)
    
    bob_measurements = measure_qubits(alice_bits, alice_bases, bob_bases, eve_present, noise_rate)
    matching_indices = compare_bases(alice_bases, bob_bases)
    
    num_test = min(len(matching_indices), max(20, len(matching_indices)//2))
    error_rate, test_indices = check_eavesdropping(alice_bits, bob_measurements, matching_indices, num_test_bits=num_test)
    
    # Store viz data for sidebar drawing later
    if QISKIT_AVAILABLE:
        st.session_state.circuit_img = draw_bb84_circuit_sample(alice_bits, alice_bases, bob_bases, num_qubits=10)
        
    st.session_state.last_error_rate = error_rate
    st.session_state.last_matched = len(matching_indices)
    st.session_state.last_keys = len(matching_indices) - len(test_indices)
        
    if error_rate > 0.10: 
        return None  # Eve intercepted!
    else:
        final_key_bits_alice = extract_key(alice_bits, matching_indices, test_indices)
        return derive_key(final_key_bits_alice)

# Sidebar for QKD Protocol control
with st.sidebar:
    st.header("1. Quantum Channel Configuration")
    num_bits = st.number_input("Number of QuBits per message", min_value=128, max_value=2048, value=256, step=128)
    
    st.markdown("---")
    st.subheader("Simulate Physics & Attacks")
    
    st.warning("Flip these toggles mid-chat to see what happens on the next message!")
    eve_present = st.checkbox("Simulate Eavesdropper (Eve)", value=False)
    noise_rate = st.slider("Environmental Noise Level", min_value=0.0, max_value=0.5, value=0.0, step=0.01, help="High noise behaves like an eavesdropper!")
    
    st.markdown("---")
    if st.button("Manually Run Key Generation"):
        st.session_state.eve_detected = False
        with st.spinner("Generating QKD Material..."):
             new_key = run_bb84(num_bits, eve_present, noise_rate)
             if new_key is None:
                 st.error(f"🚨 Eavesdropper Detected! Error rate: {st.session_state.last_error_rate:.2%}")
                 st.session_state.eve_detected = True
                 st.session_state.qkd_completed = False
             else:
                 st.success(f"Secure Key Established (Error: {st.session_state.last_error_rate:.2%})")
                 st.session_state.shared_key = new_key
                 st.session_state.qkd_completed = True
                 st.session_state.eve_detected = False

# Main Area
st.header("2. Quantum Diagnostics (Last Exchange)")
if 'last_error_rate' in st.session_state:
    st.write(f"**Last Error Rate:** {st.session_state.last_error_rate:.2%}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Qubits", num_bits)
    col2.metric("Matched Bases", st.session_state.last_matched)
    col3.metric("Keys after Test", st.session_state.last_keys)
else:
    st.info("No quantum exchange has happened yet. Send a message to generate the first keys!")

if QISKIT_AVAILABLE and 'circuit_img' in st.session_state:
    with st.expander("Show Quantum Circuit Visualization (Qiskit)", expanded=False):
        st.markdown("Displays the first 10 qubits. H-gate means Diagonal basis (+). X-gate means Bit=1.")
        st.image(st.session_state.circuit_img)

if not QISKIT_AVAILABLE:
    st.info("Qiskit is not installed or currently installing. Restart the app once it runs.")


st.markdown("---")
st.header("3. Secure Chat Interface (Continuous QKD)")
st.info("A new quantum key is established over the simulated fiber network for *every single message* sent below.")

# Display chat history first
for msg in st.session_state.chat_history:
    if msg["role"] == "System":
        with st.chat_message("System"):
            st.markdown(msg["text"])
    else:
        col1, col2 = st.columns(2)
        if msg["role"] == "Alice":
            with col1:
                with st.chat_message("Alice"):
                    if "key_preview" in msg:
                        st.markdown("**Sent by Alice 📤**")
                        st.markdown(msg["text"])
                        st.caption(f"🔑 Encrypted with Key: `{msg['key_preview']}`")
                        st.caption(f"🔒 Ciphertext: `{msg['ciphertext']}`")
                    else:
                        st.markdown("**Received by Alice 📥**")
                        st.markdown(msg["text"])
        elif msg["role"] == "Bob":
            with col2:
                with st.chat_message("Bob"):
                    if "key_preview" in msg:
                        st.markdown("**Sent by Bob 📤**")
                        st.markdown(msg["text"])
                        st.caption(f"🔑 Encrypted with Key: `{msg['key_preview']}`")
                        st.caption(f"🔒 Ciphertext: `{msg['ciphertext']}`")
                    else:
                        st.markdown("**Received by Bob 📥**")
                        st.markdown(msg["text"])

st.markdown("---")
# Input areas for Alice and Bob
col_input1, col_input2 = st.columns(2)

with col_input1:
    with st.form("alice_form", clear_on_submit=True):
        alice_prompt = st.text_input("Send a secure message as Alice...")
        alice_submit = st.form_submit_button("Alice Send")

with col_input2:
    with st.form("bob_form", clear_on_submit=True):
        bob_prompt = st.text_input("Send a secure message as Bob...")
        bob_submit = st.form_submit_button("Bob Send")

prompt = None
sender = None
recipient = None

if alice_submit and alice_prompt:
    prompt = alice_prompt
    sender = "Alice"
    recipient = "Bob"
elif bob_submit and bob_prompt:
    prompt = bob_prompt
    sender = "Bob"
    recipient = "Alice"

if prompt:
    # 1. Attempt to generate a NEW key for this specific message.
    with st.chat_message("System"):
         st.write("🌌 *Establishing fresh quantum key for transmission...*")
         
    new_key = run_bb84(num_bits, eve_present, noise_rate)
    
    if new_key is None: # EAVESDROPPER DETECTED MID-CHAT!
         # Append the failure to history
         alert_msg = f"🚨 **QUANTUM CHANNEL COMPROMISED.** Message *'{prompt}'* blocked. Error rate ({st.session_state.last_error_rate:.2%}) exceeded 10% threshold. The presence of an eavesdropper collapsed the states."
         st.session_state.chat_history.append({"role": "System", "text": alert_msg})
         st.session_state.eve_detected = True
         st.session_state.qkd_completed = False
         st.rerun() # Refresh the UI immediately to show the error
         
    else:
         # Key generated securely
         st.session_state.shared_key = new_key
         st.session_state.qkd_completed = True
         st.session_state.eve_detected = False
         
         # 2. Encrypt the message with the fresh key
         iv, ciphertext = encrypt_message(st.session_state.shared_key, prompt)
         iv_b64 = base64.b64encode(iv).decode('utf-8')
         ct_b64 = base64.b64encode(ciphertext).decode('utf-8')
         key_preview_str = base64.b64encode(st.session_state.shared_key[:8]).decode() + "..."
         
         # Append Sender's attempt
         st.session_state.chat_history.append({
             "role": sender, 
             "text": prompt, 
             "ciphertext": ct_b64,
             "key_preview": key_preview_str
         })
         
         # 3. Simulate Receiver Decrypting
         decrypted_text = decrypt_message(st.session_state.shared_key, iv, ciphertext)
         
         receiver_msg = f"{decrypted_text}\n\n✅ Successfully decrypted using matching quantum key `{key_preview_str}`"
         st.session_state.chat_history.append({
             "role": recipient, 
             "text": receiver_msg,
             "ciphertext": ct_b64
         })
         st.rerun() # Refresh the UI immediately
