# chaos_consumer.py - Simulates Congestion on Partition 1

import time
from kafka import KafkaConsumer

# Configuration must match the other files
KAFKA_BROKER = 'localhost:9092'
TARGET_TOPIC = 'destination_data' 
SLOW_PARTITION = 1 # We intentionally slow down this partition

def run_chaos_consumer():
    """
    Consumer that only reads from Partition 1 and pauses for 1 second 
    per message, forcing lag to build up on that route.
    """
    print("Waiting 10 seconds for Kafka service to stabilize...")
    time.sleep(10)

    print(f"\n--- Starting CHAOS Consumer (Slowly processing Partition {SLOW_PARTITION}) ---")
    
    # CRITICAL: We only assign to the slow partition
    consumer = KafkaConsumer(
        bootstrap_servers=[KAFKA_BROKER],
        group_id='chaos-consumer-group',
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    
    # Manually subscribe ONLY to Partition 1 of the destination topic
    from kafka.structs import TopicPartition
    partition_to_monitor = TopicPartition(TARGET_TOPIC, SLOW_PARTITION)
    consumer.assign([partition_to_monitor])
    
    try:
        for message in consumer:
            # Slow processing simulation: wait 1 second
            time.sleep(1.0) 
            print(f"[CHAOS] Processed msg from P{message.partition}. Lag is high here.")
            
    except KeyboardInterrupt:
        print("\nChaos Consumer stopped.")
time.sleep(15)
if __name__ == '__main__':
    run_chaos_consumer()