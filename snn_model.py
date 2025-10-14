# snn_model.py - The NeuroRoute SNN Core Logic (Final Working Version)
from brian2 import *
import numpy as np

# A simple rate-based encoding to convert continuous metrics into spike frequency
def rate_encode(value, min_val, max_val, max_rate=100*Hz):
    """Normalize value and convert it to a spiking rate."""
    # Clip and normalize the value
    normalized = np.clip((value - min_val) / (max_val - min_val), 0, 1)
    # Invert the rate: higher congestion/latency means LOWER spike rate (discouragement)
    rate = (1.0 - normalized) * max_rate
    return rate

class NeuroRouterSNN:
    def __init__(self, simulation_time=50*ms):
        self.simulation_time = simulation_time
        defaultclock.dt = 0.1*ms
        
        # 1. Neuron Model: Simple Integrate-and-Fire (LIF)
        neuron_eqs = '''
        dv/dt = (I - v) / (10*ms) : 1 (unless refractory)
        I : 1 # Input current, driven by spikes
        '''
        
        # 2. Input/Encoding Group
        self.input_layer = PoissonGroup(2, rates=0*Hz, name='InputEncoders') # 2 inputs
        
        # 3. Decision/Output Group
        self.output_layer = NeuronGroup(2, neuron_eqs, threshold='v>1.0', reset='v=0', refractory=5*ms, method='euler', name='RouteDecisions')
        self.output_layer.I = 0.5 

        # 4. Synapses: One-to-one mapping
        self.synapses = Synapses(self.input_layer, self.output_layer, 
                                 'w : 1', on_pre='v_post += w', name='Synapses')
        self.synapses.connect(condition='i == j')
        self.synapses.w = 0.5 

        # 5. Network Setup
        self.net = Network(self.input_layer, self.output_layer, self.synapses)

        # 6. Monitoring
        self.spike_monitor = SpikeMonitor(self.output_layer, name='OutputMonitor')
        self.net.add(self.spike_monitor)

        # --- Remove all manual reset logic from forward() ---
        # The store/restore mechanism handles resetting the monitors automatically.

    def forward(self, congestion_A, congestion_B):
        """
        Takes real-world metrics, encodes them, runs the SNN, and returns a route decision.
        """
        
        # 1. Restore the initial state (clears all monitors and resets neuron states)
        self.net.restore('INITIAL_STATE') 
        
        # 2. Encode Metrics to Spike Rates
        rate_A = rate_encode(congestion_A, 0, 100)
        rate_B = rate_encode(congestion_B, 0, 100)
        
        # Apply the new rates to the input layer
        self.input_layer.rates = [rate_A, rate_B]

        # 3. Run the Simulation
        self.net.run(self.simulation_time, report='text')

        # 4. Decode the Output
        spike_counts = self.spike_monitor.count
        count_A = spike_counts[0]
        count_B = spike_counts[1]
        
        # 5. Decision Logic
        if count_A > count_B:
            decision = 0 # Route A
            score = count_A / (count_A + count_B + 1e-6)
        elif count_B > count_A:
            decision = 1 # Route B
            score = count_B / (count_A + count_B + 1e-6)
        else:
            decision = np.random.randint(2)
            score = 0.5
            
        return decision, score, count_A, count_B
    
    # --- LEARNING RULE (CORRECTED) ---
    def update_weights(self, chosen_route, latency_score, learning_rate=0.01):
        """
        Adjusts the synaptic weight (w) based on the reward (negative latency).
        
        The weight update now uses direct array indexing to avoid the SynapticSubgroup error.
        """
        # 1. Calculate Reward (High is Good, Low is Bad)
        reward = (100 - latency_score) / 100.0
        
        # 2. Determine the index of the specific weight we need to update
        # Since we connected 0->0 and 1->1, the index of the synapse is the same as the route ID.
        target_index = chosen_route
        
        # Guard against indices outside our known routes (0 or 1)
        if target_index not in [0, 1]:
             return 

        # 3. Apply the Learning Rule
        # CRITICAL FIX: Access the weight array 'w' directly from the main synapses object
        current_w = self.synapses.w[target_index] 
        dw = learning_rate * (reward - current_w)
        
        # Update the weight array element at the target index
        self.synapses.w[target_index] = current_w + dw
        
        # Print the update
        print(f"   [LEARN] Route {chosen_route}: Lag={latency_score:.0f}, Reward={reward:.2f}. New W: {self.synapses.w[target_index]:.4f}")
if __name__ == '__main__':
    # Initialize the scope, essential for clean multiple runs in Brian2
    start_scope()
    print("Initializing NeuroRoute SNN...")
    router = NeuroRouterSNN()
    
    # --- CRITICAL STEP: STORE THE INITIAL STATE ---
    # This captures the clean slate, including empty monitors
    router.net.store('INITIAL_STATE') 
    print("Initialization complete. Network state stored.")
    
    # --- Scenario 1: A is clear (10), B is congested (80) ---
    print("\n--- Scenario 1: A is clear (10), B is congested (80) ---")
    decision, score, cA, cB = router.forward(congestion_A=10, congestion_B=80)
    print(f"Metrics: A=10, B=80 | Spikes: A={cA}, B={cB} | Decision: Route {decision} (Score: {score:.2f})")
    assert decision == 0, "Expected Route 0 (A) to win"

    # --- Scenario 2: B is clear (20), A is congested (70) ---
    print("\n--- Scenario 2: B is clear (20), A is congested (70) ---")
    decision, score, cA, cB = router.forward(congestion_A=70, congestion_B=20)
    print(f"Metrics: A=70, B=20 | Spikes: A={cA}, B={cB} | Decision: Route {decision} (Score: {score:.2f})")
    assert decision == 1, "Expected Route 1 (B) to win"

    # --- Scenario 3: Both are congested, but A is slightly worse (90) ---
    print("\n--- Scenario 3: Both congested, A is slightly worse (90) ---")
    decision, score, cA, cB = router.forward(congestion_A=90, congestion_B=85)
    print(f"Metrics: A=90, B=85 | Spikes: A={cA}, B={cB} | Decision: Route {decision} (Score: {score:.2f})")
    assert decision == 1, "Expected Route 1 (B) to win"
    
    print("\nAll SNN routing logic tests passed! The core brain is functional.")