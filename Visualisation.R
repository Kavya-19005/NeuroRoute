
# 1. Setup: Install Packages (if needed)
install.packages(c("readr", "ggplot2", "dplyr"))

# 2. Load Libraries
library(readr)
library(ggplot2)
library(dplyr)

# --- Configuration ---
FILE_PATH <- "C:\\Users\\kavya\\Desktop\\VIT\\SEM 7 YEAR 4\\Foundation of data analytics\\Project\\neuro_route_metrics.csv"

# 3. Load Data
df <- read_csv(FILE_PATH)

# 4. Data Preparation: Calculate Latency (The Inverse of Reward)
# We plot the raw Lag_Score (lower is better) to show the difference clearly.
# Filter out the waiting period
df_filtered <- df %>%
  filter(Time > 0) # Exclude the initial time=0 state for cleaner plots

# 5. Visualization 1: Comparative Latency (The Main Proof)
# Shows how NeuroRoute keeps Lag/Latency low compared to Round-Robin
latency_plot <- ggplot(df_filtered, aes(x = Message_ID, y = Lag_Score, color = Policy)) +
  # Use geom_smooth for a clearer trend line, geom_point for raw data
  geom_smooth(se = FALSE, linewidth = 1.2) + 
  geom_point(alpha = 0.3) +
  labs(
    title = "NeuroRoute vs. Round-Robin: System Lag Under Chaos",
    y = "Partition Lag (Queue Length - LOWER IS BETTER)",
    x = "Message Index (Time)",
    color = "Routing Policy"
  ) +
  scale_color_manual(values = c("neuroroute" = "#0072B2", "round_robin" = "#D55E00")) + # Colorblind friendly palette
  theme_minimal()

print(latency_plot)
# Save the plot for your presentation
# ggsave("latency_comparison.png", plot = latency_plot, width = 8, height = 5)

# 6. Visualization 2: SNN Learning Proof (Weight Convergence)
# Only plot data for the NeuroRoute trial
weights_plot <- df_filtered %>%
  filter(Policy == "neuroroute") %>%
  ggplot(aes(x = Message_ID)) +
  geom_line(aes(y = Weight_A, color = "Partition 0 Weight"), linewidth = 1) +
  geom_line(aes(y = Weight_B, color = "Partition 1 Weight"), linewidth = 1) +
  labs(
    title = "SNN Learning: Synaptic Weights Convergence",
    y = "Weight Value (Higher = Preferred)",
    x = "Message Index (Learning Step)",
    color = "Weight"
  ) +
  theme_minimal()

print(weights_plot)

# 7. Statistical Proof (Highly recommended for academic presentation)
# Check if NeuroRoute's mean lag is statistically lower than Round-Robin's
latency_nr <- df_filtered %>% filter(Policy == "neuroroute") %>% pull(Lag_Score)
latency_rr <- df_filtered %>% filter(Policy == "round_robin") %>% pull(Lag_Score)

# Perform a two-sample t-test
# H0 (Null Hypothesis): The mean lag is the same between the two policies.
# H1 (Alternative Hypothesis): NeuroRoute's lag is less than Round-Robin's.
ttest_result <- t.test(latency_nr, latency_rr, alternative = "less")

cat("\n--- Statistical T-Test Results ---\n")
print(ttest_result)
cat("\nInterpretation:\n")
cat("If the P-VALUE is < 0.05, you have statistical proof that NeuroRoute is significantly better.\n")