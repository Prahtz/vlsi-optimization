# VLSI (Very Large Scale Integration)

## Installation
To prepare the execution environment, you can simply issue the command
```
pip install -r requirements.txt
```
from this folder.

## Description
VLSI (Very Large Scale Integration) refers to the problem of integrating circuits into silicon chips. Given a fixed-width plate and a list of rectangular circuits, decide how to place them on the plate so that the length of the final plate is minimized. We will address two variants of the problem; in the first each circuit must be placed in a fixed orientation with respect to the others, while in the second case each circuit could be also rotated by 90° degrees. 

## Approaches
The problem were addressed following four different approaches:
1. CP (Constraint Programming)
2. SAT (Boolean Satisfiability problem)
3. SMT (Satisfiability Modulo Theories)
4. MIP (Mixed Integer Linear Programming)

## Data
The `data/instances/` folder contains 40 instances of the problem. They are in the format:
```
w
n
dx_1 dy_1
.
.
.
dx_n dy_n
```
where `w` is the maximum width of the plate, `n` is the number of circuits and `dx_i` and `dy_i` are the sizes of the `i`th circuit. 

## Results
You can find the results that I obtained over all the provided instances in the `results/` folder inside each folder associated with the used approach

## Documentation
In the 'docs/' folder of each approach's folder, you can find the PDF report containing all the information regarding the modelling strategies.