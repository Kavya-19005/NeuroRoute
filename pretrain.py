# pretrain.py - Supervised Pre-training for NeuroRoute SNN

import pandas as pd
import numpy as np
from snn_model import NeuroRouterSNN 
from brian2 import start_scope

# --- CONFIGURATION ---
FILE_PATH = 'Midterm_53_group.csv' 
OUTPUT_WEIGHTS_FILE = 'pretrained_weights.npz' # File to save learned weights

# Define the two paths using Source/Destination IPs found in the data
PATH_A_IP = '192.167.7.162'
PATH_B_IP = '104.91.166.75' 

def preprocess_data(file_path):
    """Loads, aggregates, and labels the network traffic data."""
    print("Loading and aggregating data...")
    
    # 1. Load Data
    # Use a chunksize to handle the large file efficiently
    chunks = pd.read_csv(file_path, chunksize=10000, usecols=['Time', 'Source', 'Destination', 'Length'])
    
    all_data = pd.DataFrame()
    for chunk in chunks:
        all_data = pd.concat([all_data, chunk], ignore_index=True)

    # Clean up column names by removing the '#' symbol if present (Wireshark output)
    all_data.columns = ['Time', 'Source', 'Destination', 'Length']
    
    # Ensure Length is numeric and handle potential errors
    all_data['Length'] = pd.to_numeric(all_data['Length'], errors='coerce').fillna(0)

    # 2. Define Time Windows (Aggregation)
    # Aggregate data into 1-second time windows
    all_data['Time_Bucket'] = (all_data['Time'] // 1).astype(int)
    
    # 3. Calculate Congestion (Lag) Scores per Path per Time Window
    
    # Total traffic for Path A (Source or Destination is Path A IP)
    is_path_A = (all_data['Source'] == PATH_A_IP) | (all_data['Destination'] == PATH_A_IP)
    # Total traffic for Path B
    is_path_B = (all_data['Source'] == PATH_B_IP) | (all_data['Destination'] == PATH_B_IP)
    
    # Aggregate total byte length (congestion) in each 1-second bucket
    lag_A = all_data[is_path_A].groupby('Time_Bucket')['Length'].sum().reset_index()
    lag_A.rename(columns={'Length': 'Lag_P0_Raw'}, inplace=True)
    
    lag_B = all_data[is_path_B].groupby('Time_Bucket')['Length'].sum().reset_index()
    lag_B.rename(columns={'Length': 'Lag_P1_Raw'}, inplace=True)
    
    # Merge the aggregated dataframes on the time bucket
    df_merged = pd.merge(lag_A, lag_B, on='Time_Bucket', how='outer').fillna(0)

    # 4. Normalize and Create Target Label
    
    # Normalize the Lag Scores to a 0-100 range for the SNN
    max_lag = df_merged[['Lag_P0_Raw', 'Lag_P1_Raw']].max().max()
    if max_lag == 0: max_lag = 1.0
    
    df_merged['Lag_P0'] = (df_merged['Lag_P0_Raw'] / max_lag) * 100
    df_merged['Lag_P1'] = (df_merged['Lag_P1_Raw'] / max_lag) * 100

    # Create Target Label: Optimal_Route (0 if P0 is better/lower lag, 1 otherwise)
    df_merged['Optimal_Route'] = np.where(
        df_merged['Lag_P0'] < df_merged['Lag_P1'], 
        0, 
        1
    )
    
    print(f"Data aggregation successful. Samples for training: {len(df_merged)}")
    return df_merged[['Lag_P0', 'Lag_P1']], df_merged['Optimal_Route']


def execute_pretraining():
    
    # 1. Load and Process Data
    inputs, labels = preprocess_data(FILE_PATH)
    
    print("\n--- 2. Initializing SNN and Training ---")
    start_scope()
    router = NeuroRouterSNN()
    
    # 3. Execute the supervised training method (requires a train function in snn_model.py)
    # NOTE: You MUST add the pretrain_model function to snn_model.py first!
    router.pretrain_model(inputs, labels, epochs=20, learning_rate=0.01)
    
    # 4. Save Pre-trained Weights
    # Save the trained weights for loading into the benchmark
    weights = {
        'W0': router.synapses.w[0],
        'W1': router.synapses.w[1]
    }
    np.savez(OUTPUT_WEIGHTS_FILE, **weights)
    print(f"\nPre-trained weights saved to {OUTPUT_WEIGHTS_FILE}")


if __name__ == '__main__':
    execute_pretraining()