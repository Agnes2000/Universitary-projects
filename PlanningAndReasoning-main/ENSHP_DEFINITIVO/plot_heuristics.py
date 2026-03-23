import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("enhsp_results.csv")

fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Stati valutati
axs[0,0].bar(df['heuristic'], df['states'])
axs[0,0].set_title('States Evaluated')

# Tempo di ricerca (ms)
axs[0,1].bar(df['heuristic'], df['time'])
axs[0,1].set_title('Search Time (ms)')

# Lunghezza piano
axs[1,0].bar(df['heuristic'], df['plan_length'])
axs[1,0].set_title('Plan Length')

# Metric
axs[1,1].bar(df['heuristic'], df['metric'])
axs[1,1].set_title('Metric')

plt.tight_layout()
plt.show()
