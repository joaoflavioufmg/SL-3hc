
# A Hierarchical Location-Allocation Model for Municipal Healthcare Planning in the Brazilian Unified Health System

Supplementary material for the manuscript entitled "A Hierarchical Location-Allocation Model for Municipal Healthcare Planning in the Brazilian Unified Health System". Reference: .

This project uses the **GLPK (GNU Linear Programming Kit)** to solve a health facility location problem in the municipality of Sete Lagoas – MG. The model was built based on equity, coverage, cost, and installed capacity criteria, aiming at the rational organization of the Primary Health Care Network (APS).

---

## 📁 Project Structure


```
Planejamento_APS_SeteLagoas/
├── model/
│   └── hc.mod
├── data/
│   └── SL.dat
├── img/
│   └── novas_UBS.png
├── README.md
```


---

## 📌 Objective

To propose a health facility location plan that meets population demand while respecting geographic coverage and team capacity criteria, with a primary focus on Primary Health Care (APS).

---

## ▶️ How to Run

1. Install GLPK: https://www.gnu.org/software/glpk/

2. Run in the terminal:

```bash
glpsol -m hc.mod -d SL.dat --cuts
```

---

## 📊 Modeling Results

### Analysis of Results

The optimal solution respects the model's constraints and guarantees universal APS coverage. The main results are presented below:

### Financial Characterization

**APS Cost:** R$ 105.851.181,35 (investiment need of R$ 15.451.205,35)

| Parameters (*optimisation results)    | Value (R$)         |
|-------------------------------------------|--------------------|
| Municipal revenue (2025)               | 1,635,941,154.00      |
| Health budget (2025)               | 583,933,738.00      |
| Medium-to-High Complexity Budget (2025)  | 412,423,111.00      |
| MAC Budget (adjusted for model) (2025)  | 282,993,086.00      |
|-------------------------------------------|--------------------|
| PHC – Primary Care Budget (2025)       | 90,399,976.00     |
|-------------------------------------------|--------------------|
| *Logistics Cost                            | 491,250.15         |
| *Fixed Costs for Existing Units [E]         | 42,900,000.00      |
| *Fixed Costs for New Units [C]              | 9,360,000.00         |
| *Cost of New Staff [C]                   | 8,698,519.20         |
| *Variable Cost                              | 44,401,412.00     |
|-------------------------------------------|--------------------|
| *PHC – Primary Care Cost (2025)       | 105,851,181.35     |
|-------------------------------------------|--------------------|

---

### New Units Created

12-15 candidate locations were selected (On Monte Carlo Simulation).

![Figura – Localização das Novas Unidades de Atenção Primária](img/novas_UBS.png)

---

### New Teams

15 new teams were allocated.

| Unidade | Nº eSFs | ME1 | EF1 | TE1 | ACS | DE1 | TD1 |
|---------|---------|-----|-----|-----|-----|-----|-----|
| PHC56   | 2       | 2   | 2   | 2   | 8   | 2   | 2   |
| PHC57   | 1       | 1   | 1   | 1   | 4   | 1   | 1   |
| ...     | ...     | ... | ... | ... | ... | ... | ... |

---

### Existing Teams

- Good distribution of physicians, nurses, and technicians
- Deficit in Oral Health Teams
- Uneven distribution of CHWs (ACS)
- eMulti stable and strengthened by federal policies

---

### Capacity Utilization

#### APS – Utilization close to 100%

| Unidade | Capacidade Total | Utilizada | % |
|---------|------------------|-----------|----|
| PHC1    | 3000             | 3000      |100%|
| PHC2    | 6000             | 6000      |100%|
| ...     | ...              | ...       |... |

*Note: There is some slack if the ceiling of 3,500 people per UBS is used.*

#### SHC – Underutilization of 2% to 75%
#### THC – High underutilization, but explained by model limitations

---

## 📜 License

MIT

## ✉️ Contact
João Flávio F. Almeida  
📧 [joao.flavio@dep.ufmg](mailto:joao.flavio@dep.ufmg)

Thiago Mendanha  
📧 [mbm.thiago@gmail.com](mailto:mbm.thiago@gmail.com)
