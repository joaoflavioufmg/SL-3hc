import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Load inflation dataset
df = pd.read_csv("inflation_scenarios_results/inflation_scenarios.csv")

# Convert costs to Millions R$
cols_to_m = [
    'Total_Cost', 'Variable_Cost', 'Fixed_Cost_Existing', 
    'Fixed_Cost_New', 'New_Team_Cost', 'Logistic_Cost'
]
for col in cols_to_m:
    df[f'{col}_M'] = df[col] / 1e6

# Format x-axis labels with cost increase percentage and unit facility fixed cost (FC1)
df['Label'] = df.apply(
    lambda r: f"+{r['Cost_Increase_Pct']}%\n(FC1 = R$ {r['FC1_Value']/1e3:.0f}k)", 
    axis=1
)

# Figure setup
fig, ax = plt.subplots(figsize=(8.0, 5.5), dpi=300)

x = df['Label']
width = 0.48

# Color palette for cost components
layers = [
    ('Variable_Cost_M', 'Variable Cost', '#2b5c8f'),
    ('Fixed_Cost_Existing_M', 'Fixed Cost (Existing PHCs)', '#4682b4'),
    ('Fixed_Cost_New_M', 'Fixed Cost (New PHCs)', '#e67e22'),
    ('New_Team_Cost_M', 'New Team Cost', '#2ecc71'),
    ('Logistic_Cost_M', 'Logistic Cost', '#e74c3c'),
]

# Stacked bar construction
bottom = pd.Series([0.0] * len(df))

for col, label, color in layers:
    ax.bar(x, df[col], bottom=bottom, label=label, color=color, width=width)
    bottom += df[col]

# Annotate total cost and percentage growth relative to base on top of each bar
base_cost = df['Total_Cost_M'].iloc[0]
for idx, row in df.iterrows():
    tot = row['Total_Cost_M']
    pct_diff = ((tot - base_cost) / base_cost) * 100
    diff_str = f" (+{pct_diff:.1f}%)" if idx > 0 else " (Base)"
    ax.text(
        idx, tot + 5, f"R$ {tot:.1f}M\n{diff_str}",
        ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1a1a1a'
    )

# Reserve upper headroom (530M limit) to accommodate legend on top-left without bar overlap
ax.set_ylim(0, 530)
ax.set_ylabel("Total Network Cost (Millions R$)", fontweight='bold')
ax.set_xlabel("Fixed Cost Inflation Scenario (% Unit Cost Increase)", fontweight='bold', labelpad=8)
ax.set_title("Sensitivity Analysis: Impact of Fixed Cost Inflation on Total Budget", pad=12, fontweight='bold')

# Legend positioned on top left
ax.legend(
    loc='upper left',
    frameon=True,
    facecolor='white',
    edgecolor='#cccccc',
    framealpha=0.95
)

ax.grid(axis='x')
plt.tight_layout()

# Save chart
plt.savefig("inflation_scenarios_results/inflation_scenarios_chart.png", dpi=300, bbox_inches='tight')
plt.close(fig)