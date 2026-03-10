import numpy as np
import hashlib

def generate_random_bits(length):
    """Generate a sequence of random bits (0s and 1s)."""
    return np.random.randint(2, size=length).tolist()

def generate_random_bases(length):
    """Generate a sequence of random bases ('+' or 'x')."""
    return np.random.choice(['+', 'x'], size=length).tolist()

def encode_qubits(bits, bases):
    """
    Simulate qubit encoding.
    Returns the same list, but just visual representation.
    In real life this would be polarized photons.
    + basis, bit 0 -> 0 deg
    + basis, bit 1 -> 90 deg
    x basis, bit 0 -> 45 deg
    x basis, bit 1 -> 135 deg
    """
    qubits = []
    for bit, basis in zip(bits, bases):
        if basis == '+':
            if bit == 0:
                qubits.append('0°')
            else:
                qubits.append('90°')
        elif basis == 'x':
            if bit == 0:
                qubits.append('45°')
            else:
                qubits.append('135°')
    return qubits

def measure_qubits(alice_bits, alice_bases, bob_bases, eve_present=False, noise_rate=0.0):
    """
    Simulate Bob measuring the qubits.
    If Eve is present, she intercepts and measures with random bases,
    then resends to Bob according to her measurement.
    If Eve measures in wrong basis, she collapses the state to that basis,
    introducing a 50% error when Bob measures in the correct basis.
    We also add basic channel noise simulation (bit flips).
    """
    if eve_present:
        # Eve intercepts
        eve_bases = generate_random_bases(len(alice_bits))
        eve_measurements = []
        for a_bit, a_base, e_base in zip(alice_bits, alice_bases, eve_bases):
            if a_base == e_base:
                bit = a_bit
            else:
                bit = np.random.randint(2)
            
            # channel noise to Eve
            if np.random.random() < noise_rate:
                bit = 1 - bit
            eve_measurements.append(bit)
        
        # Bob now measures Eve's sent qubits
        bob_measurements = []
        for e_bit, e_base, b_base in zip(eve_measurements, eve_bases, bob_bases):
            if e_base == b_base:
                bit = e_bit
            else:
                bit = np.random.randint(2)
            
            # channel noise from Eve to Bob
            if np.random.random() < noise_rate:
                bit = 1 - bit
            bob_measurements.append(bit)
        return bob_measurements
    else:
        # No Eve
        bob_measurements = []
        for a_bit, a_base, b_base in zip(alice_bits, alice_bases, bob_bases):
            if a_base == b_base:
                bit = a_bit
            else:
                bit = np.random.randint(2)
                
            if np.random.random() < noise_rate:
                bit = 1 - bit
                
            bob_measurements.append(bit)
        return bob_measurements

def compare_bases(alice_bases, bob_bases):
    """Alice and Bob compare bases publicly. Return list of matching indices."""
    matching_indices = []
    for i, (a_base, b_base) in enumerate(zip(alice_bases, bob_bases)):
        if a_base == b_base:
            matching_indices.append(i)
    return matching_indices

def check_eavesdropping(alice_bits, bob_bits, matching_indices, num_test_bits=10):
    """
    Randomly select a subset of indices from the matched bases to check for errors.
    """
    if len(matching_indices) < num_test_bits:
        num_test_bits = len(matching_indices)
    
    # Pick random subset to test
    test_indices = np.random.choice(matching_indices, size=num_test_bits, replace=False)
    
    errors = 0
    for idx in test_indices:
        if alice_bits[idx] != bob_bits[idx]:
            errors += 1
            
    error_rate = errors / num_test_bits if num_test_bits > 0 else 0
    return error_rate, test_indices.tolist()

def extract_key(bits, matching_indices, test_indices):
    """Extract the final key bits by discarding the tested bits."""
    key_bits = []
    for idx in matching_indices:
        if idx not in test_indices:
            key_bits.append(bits[idx])
    return key_bits

def derive_key(key_bits):
    """
    Convert sequence of bits into a 256-bit AES key.
    We hash the bits using SHA-256 to ensure it's a valid 32-byte key.
    """
    bit_string = ''.join(map(str, key_bits))
    # Using SHA-256 ensures we get exactly 32 bytes (256 bits)
    hash_object = hashlib.sha256(bit_string.encode('utf-8'))
    return hash_object.digest()

