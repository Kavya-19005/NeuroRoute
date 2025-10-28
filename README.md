**=== NeuroRoute: Brain-Inspired Adaptive Data Routing ===**

NeuroRoute is an innovative big data infrastructure project that uses a Spiking Neural Network (SNN) to intelligently route data streams. It replaces static, failure-prone routing rules with a system that learns and 
adapts in real-time to avoid congestion, much like the human brain redirects impulses around damaged areas.

**1. Key Project Achievements :**
  - Adaptive Routing: Implements a closed-loop Reinforcement Learning (RL) system that dynamically adjusts traffic based on measured latency and lag.
  - Dual-Phase Learning: Combines Supervised Pre-training (using a real network dataset) with Online RL for immediate, intelligent deployment.
  - Full Stack MVP: Integrates Big Data (Kafka principles), Monitoring (Prometheus principles), and Neuromorphic Computing (Brian2/SNN) in a single system design.
  - Validated Result: Achieves a >10% improvement in system efficiency (lower latency) under simulated chaos compared to the static Round-Robin baseline.

**2. Codebase Overview**
  - snn_model.py: The Brain. Contains the SNN structure, the pretrain_model for dataset loading, the forward (decision) pass, and the core update_weights (Reinforcement Learning) rule.
  - pretrain.py: The Offline Training Script. Loads the real-world network traffic dataset, processes it to define optimal routes, and runs the SNN's initial supervised training to create smart starting weights (pretrained_weights.npz).
  - benchmark.py: The Validator. This is the main execution script. It loads the pre-trained SNN, runs two controlled trials (NeuroRoute vs. Round-Robin), logs all results to the CSV file, and calculates the final performance gain.
  - baseline_router.py: The Control Group. Implements the simple, non-adaptive Round-Robin routing policy for comparison.
  - neuro_route_metrics.csv: The Result File. The final output file containing all raw data for R analysis and visualization.

**3. Setup and Execution (Offline Validation)**

  To reproduce the validated academic results, run the project in Offline Validation Mode. This bypasses local network issues while simulating the chaotic environment needed to prove the SNN's adaptability.

A. Requirements
  - Python 3.8+
  - Dependencies: You must run pip install pandas numpy brian2 kafka-python requests.
  - The pre-trained weights file (pretrained_weights.npz) must be present (created by running pretrain.py).
  
B. Execution Steps
  - Run Pre-training: (Necessary only once to create the weights file) [python pretrain.py]
  - Run Validation: Execute the final benchmark script. This executes the full Offline Chaos Test and generates the final data. [python benchmark.py]
  - Analyze Results: The final data is saved to neuro_route_metrics.csv. Use RStudio to load this file and generate the Comparative Lag and Weight Convergence plots to visualize the 10.55% efficiency improvement.
