# router_proxy.py - The NeuroRoute Router Proxy (Traffic Control Center)
import time
import json
import random
from metrics_scraper import get_realtime_metrics
from kafka import KafkaConsumer, KafkaProducer
# We import the Brain we built in the last step!
from snn_model import NeuroRouterSNN 
from brian2 import second # Needed for the SNN's internal mechanics

# --- Configuration (The Addresses) ---
KAFKA_BROKER = 'localhost:9092'
INGRESS_TOPIC = 'ingress_data'       # Where new data (cars) arrive
DESTINATION_TOPIC = 'destination_data' # The topic we route to

# We only route between Partition 0 and Partition 1 for this MVP
SNN_CANDIDATE_PARTITIONS = [0, 1] 

def run_test_producer():
        print("\n--- Running Test Producer (The car injector) ---")
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: str(v).encode('utf-8')
        )
        for i in range(20):
            message = f"Data_Packet_{i:02d}"
            producer.send(INGRESS_TOPIC, value=message)
            print(f"Produced: {message} to {INGRESS_TOPIC}")
            time.sleep(0.2)
        producer.flush()
        print("Test Producer finished.")
    

class NeuroRouterProxy:
    def __init__(self):
        print("Initializing NeuroRoute Proxy...")
        
        # 1. Initialize SNN (The Brain)
        self.router_snn = NeuroRouterSNN() 
        # Save the clean starting state (resets monitors automatically)
        self.router_snn.net.store('INITIAL_STATE') 
        
        # 2. Kafka Setup: The Listener (Consumer) and Sender (Producer)
        self.consumer = KafkaConsumer(
            INGRESS_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest', 
            enable_auto_commit=True,
            group_id='neuroroute-proxy-group'
        )
        self.producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            # Convert Python dictionary data to JSON bytes for Kafka
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka Producer (Sender)/Consumer (Listener) ready.")

    def get_routing_decision(self):
            """
            Gathers real-time lag metrics from Prometheus and feeds them to the SNN.
            """
            real_time_metrics = get_realtime_metrics()

            congestion_A = real_time_metrics.get(0, 100) 
            congestion_B = real_time_metrics.get(1, 100)

            # Pass scores to the SNN
            decision_index, score, spikes_A, spikes_B = self.router_snn.forward(
                congestion_A=congestion_A, 
                congestion_B=congestion_B
            )

            chosen_partition = SNN_CANDIDATE_PARTITIONS[decision_index]

            print(f" -> Metrics (Lag): A={int(congestion_A)}, B={int(congestion_B)} | Spikes: A={spikes_A}, B={spikes_B} | Chosen Partition: {chosen_partition}")
            return chosen_partition

    def run(self):
        print(f"Listening for messages on topic: {INGRESS_TOPIC}...")
        for message in self.consumer:
            
            # 1. DECIDE
            target_partition = self.get_routing_decision()
            
            # 2. FORWARD
            # ... (producer.send and metadata check remains here) ...
            
            # --- 3. LEARN (The Closed Loop) ---
            # Get the measured lag score for the partition that was chosen
            current_lag_metrics = get_realtime_metrics()
            
            # We use the lag/offset from Prometheus as the latency score
            latency_score = current_lag_metrics.get(target_partition, 100) 
            
            # Tell the SNN the result of its decision
            self.router_snn.update_weights(
                chosen_route=target_partition, 
                latency_score=latency_score
            )
            
            time.sleep(0.5) # Pause slightly

if __name__ == '__main__':
    # Function to simulate data traffic (cars entering the system)
    
    # --- NEURO ROUTE PROXY STARTUP ---
    print("\n\n--- STARTING NEURO ROUTE PROXY ---")
    
    try:
        router = NeuroRouterProxy()
        # The router will now wait for messages
        router.run() 
    except KeyboardInterrupt:
        print("\nNeuroRoute Proxy shut down gracefully.")
    except Exception as e:
        print(f"\nFATAL ERROR: Could not start or connect to Kafka: {e}")


# IMPORTANT: YOU WILL RUN THE PROXY AND THE PRODUCER IN SEPARATE TERMINALS!