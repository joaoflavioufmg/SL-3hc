#############################################################################
# Integrated planning for public health care
# Team: Joao Flavio de Freitas Almeida <joao.flavio@dep.ufmg.br>
# Thiago Mendanha Bahia Moura <mbm.thiago@gmail.com>
# Tasso A. T. Pimenta <tassoossat842@gmail.com>
# Messias Inácio Silva Carvalho <carvalhoisilva2023@gmail.com>
# Bruno Martins Moreira <bmmoreira@gmail.com>
# LEPOINT: Laboratorio de Estudos em Planejamento de Operacoes Integradas
# Pos Graduacao em Engenharia de Producao - PPGEP - DEP - EE - UFMG
# Universidade Federal de Minas Gerais - Escola de Engenharia
#############################################################################
# Health Care Facility Location Problem: Considering fixed facilities, 
# choose intermediate facilities accorting a criteria that improve service
# quality. Consider health care teams. 
#############################################################################
# glpsol -m hc.mod -d SL.dat --cuts 

set I:= 1..128; # The set of demand points.

set K:= 1..3; # Health care levels (PHC, SHC, THC)

param Dmax{K}; # Maximal distance (or travel time)

set P:= 1..2; # Types of Patients (chronic or acute) 

set E{K}; # Health care team from level k 

set EL{K}; # EXISTING health care units on three levels

set CL{K}; # CANDIDADE health care LOCATIONS on three levels

set L{k in K} := EL[k] union CL[k]; 

set S:={1,2,3}; # Scenarios for (1) low, (2) Medium or (3) High Chronic Burden
param Scenario default 2; # Selected chronic burden scenario: 1=low, 2=medium, 3=high
################################################
param CE1{c1 in E[1]}; # Team cost K1 ($/year)
param CE2{c2 in E[2]}; # Team cost K2 ($/year)
param CE3{c3 in E[3]}; # Team cost K3 ($/year)

param D1{I,L[1]}:=round(Uniform(1,20));    # The travel time between i and level-1 PCF.   (min)
param D2{L[1],L[2]}:=round(Uniform(1,25)); # The travel time between candidate L1 and L2. (min)
param D3{L[2],L[3]}:=round(Uniform(1,10)); # The travel time between candidate L2 and L3. (min)

set Link1 dimen 2:= setof{i in I, j1 in L[1]: D1[i,j1] <= Dmax[1]}(i,j1);
set H1:= setof{i in I,j1 in L[1]: D1[i,j1] <= Dmax[1]} j1;
set Link2 dimen 2:= setof{j1 in L[1], j2 in L[2]: D2[j1,j2] <= Dmax[2]}(j1,j2);
set H2:= setof{j1 in L[1], j2 in L[2]: D2[j1,j2] <= Dmax[2]} j2;
set Link3 dimen 2:= setof{j2 in L[2], j3 in L[3]: D3[j2,j3] <= Dmax[3]}(j2,j3);
set H3:= setof{j2 in L[2], j3 in L[3]: D3[j2,j3] <= Dmax[3]} j3;

set L1:= L[1] inter H1;
set L2:= L[2] inter H2;
set L3:= L[3] inter H3;

################################################
param TC1{I,L[1]}:= max(0.66, Normal(2.38, 1.22)); #  := Normal(2.38, 1.22) Travel cost/pat p, from demand point i to L1   ($/min)
param TC1_mean := (sum{i in I, j1 in L[1]} TC1[i,j1])/(card(I)*card(L[1]));
param TC1_sd := 
    sqrt((sum{i in I, j in L[1]} (TC1[i,j] - TC1_mean)^2) 
          / (card(I) * card(L[1])) );
# display TC1_mean, TC1_sd;

param TC2{L[1],L[2]}:= max(0.6, Normal(1.63, 0.90)); #  := Normal(1.63, 0.90) Travel cost/pat p, from L1 to L2            ($/min)
param TC2_mean := sum{j1 in L[1], j2 in L[2]} TC2[j1,j2]/(card(L[1])*card(L[2]));
param TC2_sd := 
    sqrt((sum{j1 in L[1], j2 in L[2]} (TC2[j1,j2] - TC2_mean)^2) 
          / (card(L[1]) * card(L[2])) );
# display TC2_mean, TC2_sd;

param TC3{L[2],L[3]}:= max(0.06, Normal(0.78, 0.44)); #  := Normal(0.78, 0.44) Travel cost/pat p, from L2 to L3            ($/min)
param TC3_mean := sum{j2 in L[2], j3 in L[3]} TC3[j2,j3]/(card(L[2])*card(L[3]));
param TC3_sd := 
    sqrt((sum{j2 in L[2], j3 in L[3]} (TC3[j2,j3] - TC3_mean)^2) 
          / (card(L[2]) * card(L[3])) );
# display TC3_mean, TC3_sd;

param VC1{P,L[1]} := 195.25; # 42.9 - 1.87 (FC) milhóes / 227 mil hab. | Variable cost of PHC j / pop h ($/pop)
param VC2{P,L[2]} := 881.55; # (105 milhões *0,85 / (227 mil hab * O1=0,446)). | Variable cost of SHC j / pop h ($/pop)
param VC3{P,L[3]} := 1781.71; # 91.7 milhões - (2*12.25 milhões FC) / (227 mil hab * O1=0,089*2)). | Variable cost of THC j / pop h ($/pop)

param FC1{L[1]} := 1014000.0; # (13000 USD * 5)*12. Fixed cost per period for operating PHC j    ($/year)
param FC2{L[2]} := 1125000; # 105 M * 0,15 / 14 Fixed cost per period for operating SHC j    ($/year)
param FC3{L[3]} := 12250000; # Fixed cost per period for operating THC j    ($/year)

# param PP{P}; # Proportion of patients 1 # Cronic conditions and 2 # Acute conditions

# Declare PP[1] with the uniform distribution
param PP1 := Uniform(0.60, 0.75);
param PP{i in P} := if i == 1 then PP1 else (1-PP1);
# display PP;

param POP{I}; # Proportion of patients 1 # Cronic conditions and 2 # Acute conditions
param W{i in I,p in P} := round(POP[i] * PP[p]); # The population size of type p at demand point i (pop)
# display W;

param MS1{E[1], s in S}; # Ministry of Health parameter for requirements PHC (prof/pop)
param MS2{E[2]}; # Ministry of Health parameter for requirements SHC (prof/pop)
param MS3{E[3]}; # Ministry of Health parameter for requirements THC (prof/pop)

param CNES1{E[1],EL[1]}; # Health professional teams PHC at location L1 (prof)
param CNES2{E[2],EL[2]}; # Health professional teams PHC at location L2 (prof)
param CNES3{E[3],EL[3]}; # Health professional teams PHC at location L3 (prof)

# Service operating capacity at IHC j
# param eSF_POP := 3000;
param C1{P,L[1]}; # The capacity of a level-1 PCF in K. (pop)
# The capacity of a level-2 PCF in J.   (pop)
#  5% to 15% is GP
param C2{j in L[2]} := (0.10*CNES2['ME2',j])/MS2['ME2']; 
# display C2;
#  5% to 15% is GP
param C3{j in L[3]} := (0.05*CNES3['ME3',j])/MS3['ME3'];  # The capacity of a level-3 PCF in J.   (pop)
# display C3;
param U{K}; # The number of UNITS level-k to be established. (unit)

# param O1{L[1]} := 0.446; # The proportion of patients in a L-1 to a L-2 PCF. (%)
# param O2{L[2]} := 0.089; # The proportion of patients in a L-1 to a L-2 PCF. (%)

param O1{L[1]} := Uniform(0.40, 0.50); # The proportion of patients in a L-1 to a L-2 PCF. (%)
param O2{L[2]} := Uniform(0.05, 0.15); # The proportion of patients in a L-1 to a L-2 PCF. (%)
# display O1;
# display O2;

#################################################
##var y{i in I, j1 in L1}, >=0, binary; # 1, if Pop is ASSIGNED to L-1 PCF (1) or not (0)
var y{i in I, j1 in L1} >= 0, <= 1;
var y1{j1 in L1}, >=0, binary; # 1, if a L-1 PCF is used (1) at loc. k. or not (0)
var y2{j2 in L2}, >=0, binary; # 1, if a L-2 SCF is used (1) at loc. k. or not (0)
var y3{j3 in L3}, >=0, binary; # 1, if a L-3 TCF is used (1) at loc. k. or not (0)

var u1{P, i in I, j1 in L1}, >=0;  # The flow p between demand point i and L1 (pop)
var u2{j1 in L1, j2 in L2}, >=0;  # The flow between L1 and L2              (pop)
var u3{j2 in L2, j3 in L3}, >=0;  # The flow between L2 and L3              (pop)

# var l1{E[1],L[1]}; # (+) Excess (or (-) Lack) of professional e on localion L1          (prof)
# var l2{E[2],L[2]}; # (+) Excess (or (-) Lack) of professional e on localion L2          (prof)
# var l3{E[3],L[3]}; # (+) Excess (or (-) Lack) of professional e on localion L3          (prof)

var l1{E[1],L1}; # (+) Excess (or (-) Lack) of professional e on localion L1          (prof)
var l2{E[2],L2}; # (+) Excess (or (-) Lack) of professional e on localion L2          (prof)
var l3{E[3],L3}; # (+) Excess (or (-) Lack) of professional e on localion L3          (prof)


var Unserved{i in I, p in P} >= 0; # Population NOT assigned to any PHC (pop)
param UnservedPenalty default 1.0e5; # $/person - dominates all real cost terms

#################################################
# Minimizes social and business costs:
# the total demand-weighted travel distance (or time) +
# the total fixed costs of operating the facilities 
# (related to health care teams for each location) +
# the total variable costs / patient of operating the facilities.


minimize Total_Costs:
    # Patient transportation cost
      sum{p in P, i in I, j1 in L1}D1[i,j1]*TC1[i,j1]*u1[p,i,j1] 
    + sum{j1 in L1, j2 in L2}D2[j1,j2]*TC2[j1,j2]*u2[j1,j2]  
    + sum{j2 in L2, j3 in L3}D3[j2,j3]*TC3[j2,j3]*u3[j2,j3] 
    # Cost of existing unit (including staff)
    + sum{j1 in EL[1] inter L1}FC1[j1]*y1[j1] 
    + sum{j2 in EL[2] inter L2}FC2[j2]*y2[j2] 
    + sum{j3 in EL[3] inter L3}FC3[j3]*y3[j3]
    # New unit cost
    + sum{j1 in CL[1] inter L1}FC1[j1]*y1[j1] 
    + sum{j2 in CL[2] inter L2}FC2[j2]*y2[j2] 
    + sum{j3 in CL[3] inter L3}FC3[j3]*y3[j3]  
    # Cost of new staff
    + sum{j1 in CL[1] inter L1,c1 in E[1]}CE1[c1]*y1[j1] 
    + sum{j2 in CL[2] inter L2,c2 in E[2]}CE2[c2]*y2[j2] 
    + sum{j3 in CL[3] inter L3,c3 in E[3]}CE3[c3]*y3[j3]
    # Variable cost per patient
    + sum{p in P, i in I, j1 in L1}VC1[p,j1]*u1[p,i,j1] 
    + sum{p in P, j1 in L1, j2 in L2}VC2[p,j2]*u2[j1,j2]  
    + sum{p in P, j2 in L2, j3 in L3}VC3[p,j3]*u3[j2,j3]
    # Penalty for population left unserved (soft coverage - see note above)
    + UnservedPenalty * sum{i in I, p in P} Unserved[i,p];

# Fix variables of EXISTING location
s.t. F1{j1 in EL[1] inter L1}:y1[j1] = 1; 
s.t. F2{j2 in EL[2] inter L2}:y2[j2] = 1; 
s.t. F3{j3 in EL[3] inter L3}:y3[j3] = 1;


# Entire population at each demand point i must be assigned 
# to (existing and candidate) location L1 
# (pop) = (pop)
s.t. R0{i in I, p in P}:
    sum{j1 in L1} u1[p,i,j1] + Unserved[i,p] = W[i,p];


# Patients are assigned to closest health unit
s.t. R0b{i in I, j1 in L1}: sum{k in L1: D1[i,k]>D1[i,j1]}y[i,k] + y1[j1] <= 1;

# Flow balance from PHC > SHC > THC
# (pop) = (pop)
s.t. R1{j1 in L1}: sum{j2 in L2}u2[j1,j2] = O1[j1]*sum{p in P,i in I}u1[p,i,j1];
s.t. R2{j2 in L2}: sum{j3 in L3}u3[j2,j3] = O2[j2]*sum{j1 in L1}u2[j1,j2];

# Team of existing 
# (pop)*(prof/pop) - (prof) = (prof)
# (prof) = (prof)
# Uses selected Scenario for MS1 (chronic burden)
s.t. R3e{j1 in EL[1] inter L1, e1 in E[1]}: sum{p in P, i in I}u1[p,i,j1]*MS1[e1,Scenario] + l1[e1,j1] = CNES1[e1,j1];
s.t. R4e{j2 in EL[2] inter L2, e2 in E[2]}: sum{j1 in EL[1] inter L1}u2[j1,j2]*MS2[e2] + l2[e2,j2] = CNES2[e2,j2];
s.t. R5e{j3 in EL[3] inter L3, e3 in E[3]}: sum{j2 in EL[2] inter L2}u3[j2,j3]*MS3[e3] + l3[e3,j3] = CNES3[e3,j3];

# New team?
# (prof) = (prof)
s.t. R3c{j1 in CL[1] inter L1, e1 in E[1]}: sum{p in P, i in I}u1[p,i,j1]*MS1[e1,Scenario] + l1[e1,j1] = 0;
s.t. R4c{j2 in CL[2] inter L2, e2 in E[2]}: sum{j1 in L1}u2[j1,j2]*MS2[e2] + l2[e2,j2] = 0;
s.t. R5c{j3 in CL[3] inter L3, e3 in E[3]}: sum{j2 in L2}u3[j2,j3]*MS3[e3] + l3[e3,j3] = 0;

# Capacity of existing (patients)
# (pop) = (pop)
s.t. R6e{j1 in EL[1] inter L1, p in P}: sum{i in I}u1[p,i,j1] <= C1[p,j1];
s.t. R7e{j2 in EL[2] inter L2}: sum{j1 in L1}u2[j1,j2] <= C2[j2];
s.t. R8e{j3 in EL[3] inter L3}: sum{j2 in L2}u3[j2,j3] <= C3[j3];


# Activation of new units (?)
# (pop) = (pop)
s.t. R6c{j1 in L1, p in P}: sum{i in I}u1[p,i,j1] <= C1[p,j1]*y1[j1];
s.t. R7c{j2 in L2}: sum{j1 in L1}u2[j1,j2] <= C2[j2]*y2[j2];
s.t. R8c{j3 in L3}: sum{j2 in L2}u3[j2,j3] <= C3[j3]*y3[j3];

# The number of alevel-k to be established.
# (units) = (units)
s.t. R9c:  sum{j1 in CL[1] inter L1}y1[j1] <= U[1];
s.t. R10c: sum{j2 in CL[2] inter L2}y2[j2] <= U[2];
s.t. R11c: sum{j3 in CL[3] inter L3}y3[j3] <= U[3];


solve;








printf: "\n========================================\n";
printf: "Health Care Plan\n";
printf: "========================================\n";
printf: "Scenario:\t\t%d\n", Scenario;
printf: "ChronicBurden:\t\t%s\n", if Scenario=1 then "Low" else if Scenario=2 then "Medium" else "High";
printf: "PP_chronic:\t\t%.4f\n", PP[1];
printf: "Unserved_pop:\t\t%.0f\n", sum{i in I, p in P} Unserved[i,p];
printf: "Logist cost:\t\t$%15.2f\n",    
      sum{p in P, i in I, j1 in L1}D1[i,j1]*TC1[i,j1]*u1[p,i,j1] 
    + sum{j1 in L1, j2 in L2}D2[j1,j2]*TC2[j1,j2]*u2[j1,j2]  
    + sum{j2 in L2, j3 in L3}D3[j2,j3]*TC3[j2,j3]*u3[j2,j3];
printf: "Fixed cost [E]:\t\t$%15.2f\n",    
      sum{j1 in EL[1] inter L1}FC1[j1]*y1[j1] 
    + sum{j2 in EL[2] inter L2}FC2[j2]*y2[j2] 
    + sum{j3 in EL[3] inter L3}FC3[j3]*y3[j3];
printf: "Fixed cost [C]:\t\t$%15.2f\n",     
      sum{j1 in CL[1] inter L1}FC1[j1]*y1[j1] 
    + sum{j2 in CL[2] inter L2}FC2[j2]*y2[j2] 
    + sum{j3 in CL[3] inter L3}FC3[j3]*y3[j3];
printf: "New team cost [C]:\t$%15.2f\n",     
      sum{j1 in CL[1] inter L1,c1 in E[1]}CE1[c1]*y1[j1] 
    + sum{j2 in CL[2] inter L2,c2 in E[2]}CE2[c2]*y2[j2] 
    + sum{j3 in CL[3] inter L3,c3 in E[3]}CE3[c3]*y3[j3];   
printf: "Variable Cost:\t\t$%15.2f\n",    
      sum{p in P, i in I, j1 in L1}VC1[p,j1]*u1[p,i,j1] 
    + sum{p in P, j1 in L1, j2 in L2}VC2[p,j2]*u2[j1,j2]  
    + sum{p in P, j2 in L2, j3 in L3}VC3[p,j3]*u3[j2,j3];
printf: "========================================\n";
printf: "Total    Cost:\t\t$%15.2f\n", Total_Costs 
- UnservedPenalty * sum{i in I, p in P} Unserved[i,p];
printf: "========================================\n";

printf: "========================================\n";
printf: "Primary Health Care Cost (PHC):\n";
printf: "========================================\n";
printf: "Logistic cost:\t\t$%15.2f\n", 
      sum{p in P, i in I, j1 in L1} D1[i,j1] * TC1[i,j1] * u1[p,i,j1];
printf: "Fixed cost [Existing]:\t$%15.2f\n", 
      sum{j1 in EL[1] inter L1} FC1[j1] * y1[j1];
printf: "Fixed cost [New]:\t$%15.2f\n", 
      sum{j1 in CL[1] inter L1} FC1[j1] * y1[j1];
printf: "New team cost:\t\t$%15.2f\n", 
      sum{j1 in CL[1] inter L1, c1 in E[1]} CE1[c1] * y1[j1];
printf: "Variable cost:\t\t$%15.2f\n", 
      sum{p in P, i in I, j1 in L1} VC1[p,j1] * u1[p,i,j1];
printf: "========================================\n";
printf: "Total PHC Cost:\t\t$%15.2f\n", 
      sum{p in P, i in I, j1 in L1} D1[i,j1]*TC1[i,j1]*u1[p,i,j1] +
      sum{j1 in EL[1] inter L1} FC1[j1]*y1[j1] +
      sum{j1 in CL[1] inter L1} FC1[j1]*y1[j1] +
      sum{j1 in CL[1] inter L1, c1 in E[1]} CE1[c1]*y1[j1] +
      sum{p in P, i in I, j1 in L1} VC1[p,j1]*u1[p,i,j1];
printf: "========================================\n\n";


# ---------------------------------------------------------
# Secondary Health Care Cost Report (SHC)
# ---------------------------------------------------------
printf: "========================================\n";
printf: "Secondary Health Care Cost (SHC):\n";
printf: "========================================\n";
printf: "Logistic cost:\t\t$%15.2f\n", 
      sum{j1 in L1, j2 in L2} D2[j1,j2] * TC2[j1,j2] * u2[j1,j2];

printf: "Fixed cost [Existing]:\t$%15.2f\n", 
      sum{j2 in EL[2] inter L2} FC2[j2] * y2[j2];

printf: "Fixed cost [New]:\t$%15.2f\n", 
      sum{j2 in CL[2] inter L2} FC2[j2] * y2[j2];

printf: "New team cost:\t\t$%15.2f\n", 
      sum{j2 in CL[2] inter L2, c2 in E[2]} CE2[c2] * y2[j2];

printf: "Variable cost:\t\t$%15.2f\n", 
      sum{p in P, j1 in L1, j2 in L2} VC2[p,j2] * u2[j1,j2];

printf: "========================================\n";
printf: "Total SHC Cost:\t\t$%15.2f\n", 
      sum{j1 in L1, j2 in L2} D2[j1,j2] * TC2[j1,j2] * u2[j1,j2] +
      sum{j2 in EL[2] inter L2} FC2[j2] * y2[j2] +
      sum{j2 in CL[2] inter L2} FC2[j2] * y2[j2] +
      sum{j2 in CL[2] inter L2, c2 in E[2]} CE2[c2] * y2[j2] +
      sum{p in P, j1 in L1, j2 in L2} VC2[p,j2] * u2[j1,j2];
printf: "========================================\n\n";

# ---------------------------------------------------------
# Tertiary Health Care Cost Report (THC)
# ---------------------------------------------------------
printf: "========================================\n";
printf: "Tertiary Health Care Cost (THC):\n";
printf: "========================================\n";
printf: "Logistic cost:\t\t$%15.2f\n", 
      sum{j2 in L2, j3 in L3} D3[j2,j3] * TC3[j2,j3] * u3[j2,j3];

printf: "Fixed cost [Existing]:\t$%15.2f\n", 
      sum{j3 in EL[3] inter L3} FC3[j3] * y3[j3];

printf: "Fixed cost [New]:\t$%15.2f\n", 
      sum{j3 in CL[3] inter L3} FC3[j3] * y3[j3];

printf: "New team cost:\t\t$%15.2f\n", 
      sum{j3 in CL[3] inter L3, c3 in E[3]} CE3[c3] * y3[j3];

printf: "Variable cost:\t\t$%15.2f\n", 
      sum{p in P, j2 in L2, j3 in L3} VC3[p,j3] * u3[j2,j3];

printf: "========================================\n";
printf: "Total THC Cost:\t\t$%15.2f\n", 
      sum{j2 in L2, j3 in L3} D3[j2,j3] * TC3[j2,j3] * u3[j2,j3] +
      sum{j3 in EL[3] inter L3} FC3[j3] * y3[j3] +
      sum{j3 in CL[3] inter L3} FC3[j3] * y3[j3] +
      sum{j3 in CL[3] inter L3, c3 in E[3]} CE3[c3] * y3[j3] +
      sum{p in P, j2 in L2, j3 in L3} VC3[p,j3] * u3[j2,j3];
printf: "========================================\n\n";




printf: "\n\n";
printf: "New Units:\tQty\tMax*\tUse (%%)\n"; 
printf: "========================================\n";
printf: "PHC      :\t%d\t%d\t%.2f%%\n", 
sum{j1 in CL[1] inter L1}y1[j1],
U[1], ((sum{j1 in CL[1] inter L1}y1[j1])/(U[1]+1))*100; 
printf: "SHC      :\t%d\t%d\t%.2f%%\n", 
sum{j2 in CL[2] inter L2}y2[j2],
U[2], ((sum{j2 in CL[2] inter L2}y2[j2])/(U[2]+1))*100; 
printf: "THC      :\t%d\t%d\t%.2f%%\n", 
sum{j3 in CL[3] inter L3}y3[j3],
U[3], ((sum{j3 in CL[3] inter L3}y3[j3])/(U[3]+1))*100; 
printf: "========================================\n";
printf: "*Use of max. units to be established.\n";


# ====================================================================
# Machine-readable summary lines for Monte Carlo / sensitivity parsing
# ====================================================================
printf: "\nCSV_SUMMARY_START\n";
printf: "Scenario=%d\n", Scenario;
printf: "PP1=%.6f\n", PP[1];
printf: "Unserved=%.0f\n", sum{i in I, p in P} Unserved[i,p];
printf: "Logist=%.2f\n", 
    sum{p in P, i in I, j1 in L1}D1[i,j1]*TC1[i,j1]*u1[p,i,j1] 
    + sum{j1 in L1, j2 in L2}D2[j1,j2]*TC2[j1,j2]*u2[j1,j2]  
    + sum{j2 in L2, j3 in L3}D3[j2,j3]*TC3[j2,j3]*u3[j2,j3];
printf: "FixedE=%.2f\n", 
    sum{j1 in EL[1] inter L1}FC1[j1]*y1[j1] 
    + sum{j2 in EL[2] inter L2}FC2[j2]*y2[j2] 
    + sum{j3 in EL[3] inter L3}FC3[j3]*y3[j3];
printf: "FixedC=%.2f\n", 
    sum{j1 in CL[1] inter L1}FC1[j1]*y1[j1] 
    + sum{j2 in CL[2] inter L2}FC2[j2]*y2[j2] 
    + sum{j3 in CL[3] inter L3}FC3[j3]*y3[j3];
printf: "NewTeam=%.2f\n", 
    sum{j1 in CL[1] inter L1,c1 in E[1]}CE1[c1]*y1[j1] 
    + sum{j2 in CL[2] inter L2,c2 in E[2]}CE2[c2]*y2[j2] 
    + sum{j3 in CL[3] inter L3,c3 in E[3]}CE3[c3]*y3[j3];
printf: "VarCost=%.2f\n", 
    sum{p in P, i in I, j1 in L1}VC1[p,j1]*u1[p,i,j1] 
    + sum{p in P, j1 in L1, j2 in L2}VC2[p,j2]*u2[j1,j2]  
    + sum{p in P, j2 in L2, j3 in L3}VC3[p,j3]*u3[j2,j3];
printf: "TotalCost=%.2f\n", Total_Costs - UnservedPenalty * sum{i in I, p in P} Unserved[i,p];
printf: "PHC_Total=%.2f\n", 
    sum{p in P, i in I, j1 in L1} D1[i,j1]*TC1[i,j1]*u1[p,i,j1] +
      sum{j1 in EL[1] inter L1} FC1[j1]*y1[j1] +
      sum{j1 in CL[1] inter L1} FC1[j1]*y1[j1] +
      sum{j1 in CL[1] inter L1, c1 in E[1]} CE1[c1]*y1[j1] +
      sum{p in P, i in I, j1 in L1} VC1[p,j1]*u1[p,i,j1];
printf: "SHC_Total=%.2f\n", 
    sum{j1 in L1, j2 in L2} D2[j1,j2] * TC2[j1,j2] * u2[j1,j2] +
      sum{j2 in EL[2] inter L2} FC2[j2] * y2[j2] +
      sum{j2 in CL[2] inter L2} FC2[j2] * y2[j2] +
      sum{j2 in CL[2] inter L2, c2 in E[2]} CE2[c2] * y2[j2] +
      sum{p in P, j1 in L1, j2 in L2} VC2[p,j2] * u2[j1,j2];
printf: "THC_Total=%.2f\n", 
    sum{j2 in L2, j3 in L3} D3[j2,j3] * TC3[j2,j3] * u3[j2,j3] +
      sum{j3 in EL[3] inter L3} FC3[j3] * y3[j3] +
      sum{j3 in CL[3] inter L3} FC3[j3] * y3[j3] +
      sum{j3 in CL[3] inter L3, c3 in E[3]} CE3[c3] * y3[j3] +
      sum{p in P, j2 in L2, j3 in L3} VC3[p,j3] * u3[j2,j3];
printf: "NewPHC=%d\n", sum{j1 in CL[1] inter L1}y1[j1];
printf: "NewSHC=%d\n", sum{j2 in CL[2] inter L2}y2[j2];
printf: "NewTHC=%d\n", sum{j3 in CL[3] inter L3}y3[j3];
# Aggregated lack/excess (l1) for key Family Health Strategy professions
# Convention: negative = lack (shortage), positive = surplus (or required staff at new units)
printf: "l1_ME1=%.4f\n", sum{j1 in L1} l1['ME1',j1];
printf: "l1_EF1=%.4f\n", sum{j1 in L1} l1['EF1',j1];
printf: "l1_TE1=%.4f\n", sum{j1 in L1} l1['TE1',j1];
printf: "l1_DE1=%.4f\n", sum{j1 in L1} l1['DE1',j1];
printf: "l1_TD1=%.4f\n", sum{j1 in L1} l1['TD1',j1];
# Required professionals (demand * MS1) vs available CNES (existing only)
printf: "req_ME1=%.4f\n", sum{j1 in L1} sum{p in P, i in I}u1[p,i,j1]*MS1['ME1',Scenario];
printf: "req_EF1=%.4f\n", sum{j1 in L1} sum{p in P, i in I}u1[p,i,j1]*MS1['EF1',Scenario];
printf: "req_TE1=%.4f\n", sum{j1 in L1} sum{p in P, i in I}u1[p,i,j1]*MS1['TE1',Scenario];
printf: "req_DE1=%.4f\n", sum{j1 in L1} sum{p in P, i in I}u1[p,i,j1]*MS1['DE1',Scenario];
printf: "req_TD1=%.4f\n", sum{j1 in L1} sum{p in P, i in I}u1[p,i,j1]*MS1['TD1',Scenario];
printf: "cnes_ME1=%.4f\n", sum{j1 in EL[1] inter L1} CNES1['ME1',j1];
printf: "cnes_EF1=%.4f\n", sum{j1 in EL[1] inter L1} CNES1['EF1',j1];
printf: "cnes_TE1=%.4f\n", sum{j1 in EL[1] inter L1} CNES1['TE1',j1];
printf: "cnes_DE1=%.4f\n", sum{j1 in EL[1] inter L1} CNES1['DE1',j1];
printf: "cnes_TD1=%.4f\n", sum{j1 in EL[1] inter L1} CNES1['TD1',j1];
printf: "CSV_SUMMARY_END\n";
# ====================================================================
# ====================================================================








# # =========================================================
# # Operations Flow
# # =========================================================
# printf: "\n\n";
# printf: "========================================\n";
# printf: "Municipality:\t  Pop\t Flow to PHC\n"; 
# printf: "========================================\n";
# printf{i in I}: "[%-14s]: %d\t %d\n", i, 
# sum{p in P}W[i,p], 
# sum{p in P,j1 in L1}u1[p,i,j1];



# printf: "\n\n";
# printf: "========================================\n";
# printf: "Mun     > PHC   :(flow)\n";
# printf: "========================================\n";

# for{i in I}{
#     printf"M[%-4d] > \t: %d\n", i, sum{p in P}W[i,p];
#     for{j1 in L1: sum{p in P}u1[p,i,j1] > 0}{
#     printf"\t> L[%-4s]: %d\n", j1, sum{p in P}u1[p,i,j1];
#     }
# }

# printf: "\n\n";
# printf: "========================================\n";
# printf: "PHC     > SHC   :(flow)\n";
# printf: "========================================\n";

# for{j1 in L1: sum{p in P,i in I}u1[p,i,j1] > 0}{
#     printf"L[%-4s] > \t: %d\n", j1, O1[j1]*sum{p in P,i in I}u1[p,i,j1];
#     for{j2 in L2: u2[j1,j2] > 0}{
#     printf"\t> L[%-4s]: %d\n", j2, u2[j1,j2];
#     }
# }


# printf: "\n\n";
# printf: "========================================\n";
# printf: "SHC     > THC   :(flow)\n";
# printf: "========================================\n";

# for{j2 in L2: sum{j1 in L1}u2[j1,j2]>0}{
#     printf: "L[%-4s] > \t : %d\n", j2, O2[j2]*sum{j1 in L1}u2[j1,j2];
#     for{j3 in L3: u3[j2,j3] > 0}{
#         printf: "\t> L[%-4s]: %d\n", j3, u3[j2,j3];
#     }
# }

# printf: "\n\n";
# printf: "========================================\n\n";
# printf: "========================================\n";
# printf: "Health care team (Existing and New*)\n";
# printf: "========================================\n";

# printf: "========================================\n";
# printf: "PHC-Team CNES\tFlow\t(-)Lack/(+)Excess\n";
# printf: "========================================\n";

# for{j1 in EL[1] inter L1: sum{p in P,i in I}u1[p,i,j1] > 0}{
#     printf"L[%-4s]\n", j1;
#     for{e1 in E[1]}{
#     printf"  [%-s]: %.2f\t%.2f\t%.2f\n", e1, CNES1[e1,j1], 
#     sum{p in P, i in I}u1[p,i,j1]*MS1[e1,Scenario],
#     l1[e1,j1];
#     }
# }

# for{j1 in CL[1] inter L1: sum{p in P,i in I}u1[p,i,j1] > 0}{
#     printf"L[%-4s*]\n", j1;
#     for{e1 in E[1]}{
#     printf"  [%-s]: %s\t%.2f\t%.2f\n", e1, " --",
#     sum{p in P, i in I}u1[p,i,j1]*MS1[e1,Scenario],
#     l1[e1,j1];
#     }
# }



# printf: "========================================\n";
# printf: "SHC-Team CNES\tFlow\t(-)Lack/(+)Excess\n";
# printf: "========================================\n";

# for{j2 in EL[2] inter L2: sum{j1 in L1}u2[j1,j2] > 0}{
#     printf"L[%-4s]\n", j2;
#     for{e2 in E[2]}{
#     printf"  [%-s]: %.2f\t%.2f\t%.2f\n", e2, CNES2[e2,j2], 
#     sum{j1 in L1}u2[j1,j2]*MS2[e2],
#     l2[e2,j2];
#     }
# }

# for{j2 in CL[2] inter L2: sum{j1 in L1}u2[j1,j2] > 0}{
#     printf"L[%-4s*]\n", j2;
#     for{e2 in E[2]: sum{j1 in L1}u2[j1,j2]>0}{
#     printf"  [%-s]: %s\t%.2f\t%.2f\n", e2, " --", 
#     sum{j1 in L1}u2[j1,j2]*MS2[e2],
#     l2[e2,j2];
#     }
# }

# printf: "========================================\n";
# printf: "THC-Team CNES\tFlow\t(-)Lack/(+)Excess\n";
# printf: "========================================\n";

# for{j3 in EL[3] inter L3: sum{j2 in L2}u3[j2,j3] > 0}{
#     printf"L[%-4s]\n", j3;
#     for{e3 in E[3]}{
#     printf"  [%-s]: %.2f\t%.2f\t%.2f\n", e3, CNES3[e3,j3], 
#     sum{j2 in L2}u3[j2,j3]*MS3[e3],
#     l3[e3,j3];
#     }
# }

# for{j3 in CL[3] inter L3: sum{j2 in L2}u3[j2,j3] > 0}{
#     printf"L[%-4s*]\n", j3;
#     for{e3 in E[3]: sum{j2 in L2}u3[j2,j3]>0}{
#     printf"  [%-s]: %s\t%.2f\t%.2f\n", e3, " --",  
#     sum{j2 in L2}u3[j2,j3]*MS3[e3],
#     l3[e3,j3];
#     }
# }


# printf: "========================================\n";
# printf: "PHC  [p]:\tCapty\tMet\tUse(%%)\n";
# printf: "========================================\n";
# # Existing location
# printf{j1 in EL[1] inter L1, p in P}: 
# "[%-4s][%d]:\t%d\t%d\t%3d%%\n", j1, p, 
# C1[p,j1], 
# sum{i in I}u1[p,i,j1],
# ((sum{i in I}u1[p,i,j1])/(C1[p,j1]))*100;
# # Candidate location
# printf{j1 in CL[1] inter L1, p in P: sum{i in I}u1[p,i,j1]>0}: 
# "[%-4s*][%d]:\t%d\t%d\t%3d%%\n", j1, p, 
# C1[p,j1], 
# sum{i in I}u1[p,i,j1],
# ((sum{i in I}u1[p,i,j1])/(C1[p,j1]))*100;



# printf: "========================================\n";
# printf: "SHC     :\tCapty\tMet\tUse(%%)\n";
# printf: "========================================\n";
# # Existing location
# printf{j2 in EL[2] inter L2}: "[%-6s]:\t%d\t%d\t%3d%%\n", j2, 
# C2[j2], 
# sum{j1 in L1}u2[j1,j2],
# (if C2[j2] > 0 then (sum{j1 in L1}u2[j1,j2]/C2[j2])*100 else 0);

# # Candidate location
# printf{j2 in CL[2] inter L2: sum{j1 in L1}u2[j1,j2]>0}: 
# "[%-5s*]:\t%d\t%d\t%3d%%\n", j2, 
# C2[j2], 
# sum{j1 in L1}u2[j1,j2],
# (if C2[j2] > 0 then (sum{j1 in L1}u2[j1,j2]/C2[j2])*100 else 0);

# printf: "========================================\n";
# printf: "THC     :\tCapty\tMet\tUse(%%)\n";
# printf: "========================================\n";
# # Existing location
# printf{j3 in EL[3] inter L3}: "[%-6s]:\t%d\t%d\t%3d%%\n", j3, 
# C3[j3], 
# sum{j2 in L2}u3[j2,j3],
# (if C3[j3] > 0 then (sum{j2 in L2}u3[j2,j3]/C3[j3])*100 else 0);

# # Candidate location
# printf{j3 in CL[3] inter L3: sum{j2 in L2}u3[j2,j3]>0}: 
# "[%-5s*]:\t%d\t%d\t%3d%%\n", j3, 
# C3[j3], 
# sum{j2 in L2}u3[j2,j3],
# (if C3[j3] > 0 then (sum{j2 in L2}u3[j2,j3]/C3[j3])*100 else 0);
# printf: "========================================\n\n";

end;

