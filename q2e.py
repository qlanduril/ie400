import gurobipy as gp
from gurobipy import GRB

# Data Table
investments = {
    1: {'duration': 2, 'interest_rates': [0.26, 0.0, 0.26, 0.0]},   # Option 1
    2: {'duration': 1, 'interest_rates': [0.12, 0.12, 0.12, 0.12]}, # Option 2
    3: {'duration': 3, 'interest_rates': [0.19, 0.19, 0.0, 0.0]},   # Option 3
    4: {'duration': 2, 'interest_rates': [0.0, 0.27, 0.27, 0.0]},   # Option 4
    5: {'duration': 3, 'interest_rates': [0.0, 0.39, 0.0, 0.0]},    # Option 5
    6: {'duration': 2, 'interest_rates': [0.0, 0.0, 0.28, 0.0]}     # Option 6
}
initial_funds = 14000

years = [2021,2022,2023,2024,2025]

contributations = [0.4, 0.1, 0.05]

# Create a new model
m = gp.Model("maximize_P4")

m.Params.LogToConsole = 1  # Log messages to the console
m.Params.LogFile = "logfile.log"  # Log messages to a file

# Decision variables
x = m.addVars(len(investments), len(years), vtype=GRB.CONTINUOUS, name="x")
print("X value= ",x.keys())

# Create additional variables for top 3 max
max1 = m.addVar(name="max1", vtype=GRB.CONTINUOUS)
max2 = m.addVar(name="max2", vtype=GRB.CONTINUOUS)
max3 = m.addVar(name="max3", vtype=GRB.CONTINUOUS)

# Objective function
#obj_expr = gp.quicksum(x[i, len(years)-1] for i in range(len(investments))) #
obj_expr = gp.quicksum(x[i, len(years)-1] for i in range(len(investments))) + 0.4*max1 + 0.1*max2 + 0.05*max3

m.setObjective(obj_expr , GRB.MAXIMIZE)

# Constraints
for year in years:  
    if year ==2021:
        m.addConstr(gp.quicksum( x[i, year-2021] for i in range(len(investments)) ) == initial_funds )
        continue
    
    m.addConstr(gp.quicksum( x[i, year-2021] for i in range(len(investments)) ) == 
                gp.quicksum(((year-p_year) == investments[option]['duration'])*
                            (1+investments[option]['interest_rates'][p_year-2021-1])*
                            x[option-1, p_year-2021] 
                            for option in range(1, len(investments)+1 ) 
                            for p_year in years) )

# max should be bigger than all total options invested
for option in range(len(investments)):  
    m.addConstr(max1 >= gp.quicksum(x[option,year] for year in range(len(years))))

#max option invested can not exceed the possible max invest
m.addConstr(gp.quicksum(x[i, len(years)-1] for i in range(len(investments))) >= max1)

#max2 can not exceed max1
m.addConstr(max1 >= max2)

#max3 can not exceed max2
m.addConstr(max2 >= max3)
    
# Non-negativity constraint
for i in range(6):
    for j in range(5):
        m.addConstr(x[i, j] >= 0, f"non_negativity_{i}_{j}")

# Optimize model
m.optimize()

# Print solution
if m.status == GRB.OPTIMAL:
    print("Optimal solution:")
    for i in range(6):
        for j in range(4):
            print(f"x[{i+1},{j+1}] = {x[i, j].x}")
    print(f"Maximized value of P4: {m.objVal}")
else:
    print("No solution found.")