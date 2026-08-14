import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# 1. Set academic style optimized for half-page A4
sns.set_theme(style="whitegrid", font="sans-serif")

plt.rcParams.update({
    'font.size': 8.5,
    'axes.labelsize': 9.5,
    'axes.titlesize': 10.5,
    'xtick.labelsize': 8.0,
    'ytick.labelsize': 8.0,
    'legend.fontsize': 8.0,
    'legend.title_fontsize': 8.5
})

# Load dataset
long_df = pd.read_csv("chronic_scenarios_results/chronic_staffing_long.csv")

# Professional category mapping
prof_map = {
    'ME1': 'ME1 (Physician)',
    'EF1': 'EF1 (Nurse)',
    'TE1': 'TE1 (Nursing Tech)',
    'DE1': 'DE1 (Dentist)',
    'TD1': 'TD1 (Oral Health Tech)'
}

# 2. Calculate mean requirements and retrieve existing stock (CNES)
req_means = long_df.groupby(['profession', 'scenario_name'])['req'].mean().reset_index()
cnes_vals = long_df.groupby('profession')['cnes'].first().reset_index()

prof_keys = ['ME1', 'EF1', 'TE1', 'DE1', 'TD1']
scen_order = ['Low', 'Medium', 'High']
palette = {'Low': '#2b5c8f', 'Medium': '#d97724', 'High': '#c0392b'}

# 3. Plot Setup for Half-Page A4
fig, ax = plt.subplots(figsize=(6.5, 4.0), dpi=300)

x = np.arange(len(prof_keys))
width = 0.22

# Plot scenario bars
for i, scen in enumerate(scen_order):
    scen_req = [
        req_means[
            (req_means['profession'] == p) & 
            (req_means['scenario_name'] == scen)
        ]['req'].values[0] for p in prof_keys
    ]
    ax.bar(
        x + (i - 1) * width, 
        scen_req, 
        width, 
        label=f'Req ({scen})', 
        color=palette[scen], 
        alpha=0.85
    )

# Overlay CNES Existing Stock diamonds
cnes_list = [cnes_vals[cnes_vals['profession'] == p]['cnes'].values[0] for p in prof_keys]
ax.scatter(
    x, cnes_list, 
    color='black', 
    s=60, 
    zorder=5, 
    marker='D', 
    label='Existing CNES'
)

# Refactored annotations: offset to the right of the diamond marker
for idx, val in enumerate(cnes_list):
    ax.annotate(
        f'CNES: {int(val)}', 
        (x[idx] + 0.15, val),  # Shifted right by 0.15 units
        ha='left', 
        va='center', 
        fontsize=7.5, 
        fontweight='bold', 
        color='black'
    )

# 4. Axis Labels & Legend Formatting
ax.set_title(
    "Workforce Requirement ($req$) vs. Existing Facility Stock ($CNES$)", 
    pad=10, 
    fontweight='bold'
)
ax.set_xlabel("Health Professional Category", labelpad=6, fontweight='bold')
ax.set_ylabel("Number of Professionals", labelpad=6, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([prof_map[p] for p in prof_keys], rotation=12, ha='right')

# Add headroom above highest element for the top-right legend
ax.set_ylim(0, max(max(cnes_list), req_means['req'].max()) + 45)

ax.legend(
    title="Legend", 
    frameon=True, 
    facecolor='white', 
    edgecolor='gray',
    loc='upper right',
    ncol=1
)

plt.tight_layout()
plt.savefig("chronic_scenarios_results/req_vs_cnes.png", dpi=300, bbox_inches='tight')
plt.show()