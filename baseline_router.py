# baseline_router.py - Implements Static Round-Robin Routing

import itertools

class RoundRobinRouter:
    """
    Implements a simple, non-adaptive Round-Robin routing policy
    across a fixed set of partitions.
    """
    def __init__(self, candidate_partitions):
        self.partitions = candidate_partitions
        # Use itertools.cycle to continuously loop through the partition list
        self.partition_cycle = itertools.cycle(self.partitions)
        print(f"Round-Robin Router initialized for partitions: {self.partitions}")
        
    def get_routing_decision(self):
        """
        Gets the next partition ID in the sequence.
        
        It takes no metrics as input and does not learn.
        """
        # Get the next partition in the cycle
        chosen_partition = next(self.partition_cycle)
        
        # In a real benchmark, this would just return the ID, 
        # but we print for clarity.
        # print(f" -> BASELINE: Chosen Partition: {chosen_partition}")
        return chosen_partition

# The NeuroRoute SNN uses partitions [0, 1], so we stick to those for the comparison
BASELINE_PARTITIONS = [0, 1] 
# Note: For full scalability, you would use all 4 Kafka partitions [0, 1, 2, 3]

if __name__ == '__main__':
    # Simple test
    router = RoundRobinRouter(BASELINE_PARTITIONS)
    print("Testing Round-Robin decisions:")
    for _ in range(6):
        print(router.get_routing_decision())