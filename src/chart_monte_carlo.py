import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load data
df_runs = pd.read_csv("monte_carlo_results/monte_carlo_runs.csv")
df_summary = pd.read_csv("monte_carlo_results/monte_carlo_summary.csv")

# Set publication-quality style
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 8.5,
    'figure.titlesize': 12
})

costs_m = df_runs['Total_Cost'] / 1e6
mean_m = df_summary['Mean_Total_Cost'].iloc[0] / 1e6
ci_lower_m = df_summary['CI_Lower'].iloc[0] / 1e6
ci_upper_m = df_summary['CI_Upper'].iloc[0] / 1e6

fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=300)

# Histogram + KDE
n, bins, patches = ax.hist(costs_m, bins=10, density=True, alpha=0.4, color='#2b5c8f', edgecolor='black', linewidth=0.8, label='Simulation Runs')
sns.kdeplot(costs_m, ax=ax, color='#1a365d', linewidth=2, label='Kernel Density Estimate (KDE)')

# Vertical lines for Mean and 95% CI
ax.axvline(mean_m, color='#d9534f', linestyle='--', linewidth=2, label=f'Mean (R$ {mean_m:.2f}M)')
ax.axvline(ci_lower_m, color='#e67e22', linestyle=':', linewidth=1.8, label=f'95% CI Lower (R$ {ci_lower_m:.2f}M)')
ax.axvline(ci_upper_m, color='#e67e22', linestyle=':', linewidth=1.8, label=f'95% CI Upper (R$ {ci_upper_m:.2f}M)')

# Highlight 95% CI region
ax.axvspan(ci_lower_m, ci_upper_m, color='#f39c12', alpha=0.15, label='95% Confidence Interval')

# Labels and title
ax.set_xlabel("Total Network Cost (Millions R$)", fontweight='bold', labelpad=8)
ax.set_ylabel("Probability Density", fontweight='bold')
ax.set_title("Monte Carlo Uncertainty Analysis: Distribution of Total Network Cost ($N=30$ Runs)", pad=12, fontweight='bold')

# Position legend on top left
ax.legend(
    loc='upper left',
    frameon=True,
    facecolor='white',
    edgecolor='#cccccc',
    framealpha=0.95
)

plt.tight_layout()
plt.savefig("monte_carlo_results/monte_carlo_distribution.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Monte Carlo distribution chart generated successfully!")