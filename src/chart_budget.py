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

# Load dataset
df = pd.read_csv("budget_scenarios_results/budget_scenarios.csv")

# Convert costs to Millions R$
cols_to_m = [
    'Total_Cost', 'PHC_Variable', 'PHC_Fixed_Existing', 'PHC_Fixed_New',
    'PHC_New_Team', 'PHC_Logistic', 'PHC_Total', 'SHC_Total', 'THC_Total'
]
for col in cols_to_m:
    df[f'{col}_M'] = df[col] / 1e6

# Formatted x-axis labels
df['Label'] = df.apply(lambda r: f"U1 = {r['U1']}\n({r['New_Facilities']} New)", axis=1)

# Single figure setup
fig, ax = plt.subplots(figsize=(8.0, 5.5), dpi=300)

x = df['Label']
width = 0.52

# Stacking order (bottom to top):
# Detailed PHC components first, followed by SHC and THC totals
layers = [
    ('PHC_Variable_M', 'PHC: Variable Cost', '#2b5c8f'),
    ('PHC_Fixed_Existing_M', 'PHC: Fixed Cost (Existing)', '#4682b4'),
    ('PHC_Fixed_New_M', 'PHC: Fixed Cost (New)', '#e67e22'),
    ('PHC_New_Team_M', 'PHC: New Team Cost', '#2ecc71'),
    ('PHC_Logistic_M', 'PHC: Logistic Cost', '#e74c3c'),
    ('SHC_Total_M', 'SHC: Secondary Care (Total)', '#95a5a6'),
    ('THC_Total_M', 'THC: Tertiary Care (Total)', '#34495e'),
]

# Accumulate base for stacked bars
bottom = pd.Series([0.0] * len(df))

for col, label, color in layers:
    ax.bar(x, df[col], bottom=bottom, label=label, color=color, width=width)
    bottom += df[col]

# Annotate Total Cost on top of each bar
for idx, row in df.iterrows():
    tot = row['Total_Cost_M']
    ax.text(
        idx, tot + 5, f"R$ {tot:.1f}M",
        ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1a1a1a'
    )

# Extended Y-limit (520M) ensures ample room for top-left legend above initial bars
ax.set_ylim(0, 520)
ax.set_ylabel("Cost (Millions R$)", fontweight='bold')
ax.set_xlabel("Expansion Scenario ($U_1$ Limit & New PHC Facilities Built)", fontweight='bold', labelpad=8)
ax.set_title("Budget & Cost Breakdown Across Health Care Levels (PHC, SHC, THC)", pad=12, fontweight='bold')

# Position legend on top left
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
plt.savefig("budget_scenarios_results/budget_scenarios_3levels.png", dpi=300, bbox_inches='tight')
plt.close(fig)