from qiskit import QuantumCircuit
from qiskit_aer import Aer
import qiskit
import matplotlib.pyplot as plt
import os

def draw_bb84_circuit_sample(alice_bits, alice_bases, bob_bases, num_qubits=5):
    """
    Simulate the BB84 protocol using Qiskit for a small number of qubits,
    and return the path to the saved matplotlib figure.
    """
    # Restrict to a small sample for visualization purposes
    n = min(len(alice_bits), num_qubits)
    qc = QuantumCircuit(n, n)
    
    # 1. State Preparation (Alice)
    for i in range(n):
        if alice_bits[i] == 1:
            qc.x(i) # Bit 1 -> |1>
        
        if alice_bases[i] == 'x':
            qc.h(i) # Diagonal basis -> |+> or |->
            
    qc.barrier()
    
    # 2. Measurement (Bob)
    for i in range(n):
        if bob_bases[i] == 'x':
            qc.h(i) # Measure in diagonal basis
        qc.measure(i, i)
        
    # Draw circuit using matplotlib
    fig = qc.draw(output='mpl')
    
    # Ensure a directory exists for saved visuals
    img_path = 'circuit_viz.png'
    fig.savefig(img_path)
    plt.close(fig) # prevent memory leak
    
    return img_path
