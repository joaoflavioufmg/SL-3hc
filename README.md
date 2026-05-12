
# Three-Level Hierarchical Health Care Planning Model to Increase Accessibility and Equity at the Municipality Level

Supplementary material for the manuscript entitled "Planning for equitable access to integrated public health services in a Brazilian municipality", for SBPO Annals. Reference: .

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

| Parameters (*optimization results)    | Value (R$)         |
|-------------------------------------------|--------------------|
| Receita do município (2025)               | 1.635.941.154,00      |
| Orçamento para Saúde (2025)               | 583.933.738,00      |
| Orçamento Média-Alta complexidade (2025)  | 412.423.111,00      | 
| Orçamento MAC (ajustado p/ modelo) (2025)  | 282.993.086,00      | 
|-------------------------------------------|--------------------|
| PHC-Orçamento Atenção Básica (2025)       | 90.399.976,00     |
|-------------------------------------------|--------------------|
| *Custo Logístico                            | 491.250,15         |
| *Custo Fixo Unidades Existentes [E]         | 42.900.000,00      |
| *Custo Fixo Novas Unidades [C]              | 9.360.000,00         |
| *Custo de Nova Equipe [C]                   | 8.698.519,20         |
| *Custo Variável                              | 44.401.412,00     |
|-------------------------------------------|--------------------|
| *PHC-Custo Atenção Básica (2025)       | 105.851.181,35     |
|-------------------------------------------|--------------------|

---

### New Units Created

12 out of 15 candidate locations were selected.

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
