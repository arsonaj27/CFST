# Import necessary libraries
import json  # for JSON file operations
import math  # for mathematical functions
import csv   # for CSV file operations
import os    # for operating system related functionalities
import matplotlib.pyplot as plt  # for plotting
import tkinter as tk              # for GUI
from tkinter import messagebox   # for displaying message boxes

# Function to get parameters from user input
def get_parameters():
    parameters = {}  # Initialize parameters dictionary
    # Ask user for input and store values in parameters dictionary
    parameters['D'] = float(input("Enter outer diameter of steel tube (D): "))
    parameters['t'] = float(input("Enter thickness of steel tube (t): "))
    
    # Validate unconfined concrete strength (fc)
    while True:
        fc = float(input("Enter unconfined concrete strength (fc): "))
        if 15 <= fc <= 200:
            parameters['fc'] = fc
            break
        else:
            print("Unconfined concrete strength (fc) must be between 15 and 200. Please enter a valid value.")
    
    # Ask for Modulus of elasticity of concrete (Ec)
    parameters['Ec'] = float(input("Enter the Modulus of elasticity of concrete (Ec):"))

    # Validate yield stress of steel (fy)
    while True:
        fy = float(input("Enter yield stress of steel (fy): "))
        if fy < 960:
            parameters['fy'] = fy
            break
        else:
            print("Yield stress of steel (fy) must be less than 960. Please enter a valid value.")
    
    # Ask for ultimate stress of steel (fu)
    parameters['fu'] = float(input("Enter ultimate stress of steel (fu): "))
    # Ask for modulus of elasticity of steel (Es)
    parameters['Es'] = float(input("Enter modulus of elasticity of steel (Es): "))
    
    # Validate length of column (L) with respect to outer diameter
    while True:
        parameters['L'] = float(input("Enter length of column (L): "))
        if parameters['L'] / parameters['D'] <= 5:
            break
        else:
            print("Warning: Length/Outer diameter ratio should be less than or equal to 5. Please enter a valid value.")
    
    # Save parameters to a JSON file
    save_parameters(parameters)

    return parameters

# Function to save parameters to a JSON file
def save_parameters(parameters):
    with open("parameters.json", "w") as f:
        json.dump(parameters, f)

# Function to calculate various parameters related to steel
def calculate_parameters(parameters):
    # Extract parameters from the dictionary
    D = parameters['D']
    t = parameters['t']
    L = parameters['L']
    Es = parameters['Es']
    fc = parameters['fc']
    Ec = parameters['Ec']
    fy = parameters['fy']
    fu = parameters['fu']
            
    # Calculate outer diameter/thickness ratio
    outer_diameter_thickness_ratio = D / t

    # Calculate length/outer diameter ratio
    length_outer_diameter_ratio = L / D

    # Calculate cross section area of core concrete
    A_cc = math.pi * (D - 2 * t)**2 / 4
    
    # Calculate total cross section area of column
    A_total = math.pi * D**2 / 4

    # Calculate cross section area of steel
    A_s = A_total - A_cc
    
    # Calculate confinement factor
    CF = (A_s * fy) / (fc * A_cc)

    return A_s, A_total, A_cc, CF, outer_diameter_thickness_ratio, length_outer_diameter_ratio

# Get parameters from user input
parameters = get_parameters()
print("Parameters saved to parameters.json file.")

# Calculate parameters based on user input
A_s, A_total, A_cc, CF, outer_diameter_thickness_ratio, length_outer_diameter_ratio = calculate_parameters(parameters)

# Print calculated parameters
print("Parameters:")
print(f"CSA of Steel: {A_s}")
print(f"Total CSA of Column: {A_total}")
print(f"CSA of Concrete: {A_cc}")
print(f"Confinement Factor: {CF}")
print(f"Outer Diameter to Thickness Ratio: {outer_diameter_thickness_ratio}")
print(f"Length to Outer Diameter Ratio: {length_outer_diameter_ratio}")

# Function to calculate steel parameters
def calculate_steel_parameters(parameters, A_s, A_total, A_cc, Es):
    # Extract necessary parameters
    fy = parameters['fy']
    fu = parameters['fu']
    fc = parameters['fc']
    epsilon_c0 = parameters.get('epsilon_c0', 0)  # Default value for epsilon_c0
    Ec = parameters['Ec']
    CF = (A_s * fy) / (fc * A_cc)
    
    # Calculate Initial Modulus of Elasticity (Ep)
    Ep = 0.02 * parameters['Es']
    
    # Calculate Normal Strain of Steel
    epsilon_y = fy / Es
         
    # Calculate Strain at Peak Stress (epsilon_c0)
    epsilon_c0 = 0.002 * (1 + A_s / A_total * Es / Ec)  
    
    # Calculate First Peak Stress (fy_prime)
    expression = 1.02 - 0.01 * ((epsilon_y / epsilon_c0) ** 1.5) * ((parameters['D'] / parameters['t']) ** 0.5)
    if expression < 0:
        fy_prime = 0.001 * fy
    elif expression > 1:
        fy_prime = fy
    else:
        fy_prime = expression * fy
        
    # Calculate Strain Corresponding to First Peak Stress (epsilony_prime)
    epsilony_prime = fy_prime / Es
    
    # Calculate Critical Stress (fcr_prime)
    if fy_prime * (math.exp(-0.39 + 0.1 * CF + 0.06 * math.log(CF) / (CF**2))) >= fy_prime:
        fcr_prime = fy_prime
    else:
        fcr_prime = fy_prime * (math.exp(-0.39 + 0.1 * CF + 0.06 * math.log(CF) / (CF**2)))
    
    # Calculate Ultimate Strain (eu)
    if fy <= 300:
        eu = (100 * fy / Es)
    elif fy <= 800:
        eu = (100 - (0.15 * (fy - 300) * (fy / Es)))
    else:
        eu = (25 - (0.1 * (fy - 800) * fy / Es))
    
    # Calculate Critical Strain (ecr_prime)
    ey = epsilon_y
    t_D_fc = parameters['t'] / (parameters['D'] * parameters['fc'])
    expression_ecr = ey * (28 - (0.07 * CF) - (12 / (CF**0.2)) - (0.13 * (fy**0.75) * (t_D_fc**0.07)))
    if expression_ecr < ey:
        ecr_prime = ey
    elif expression_ecr > eu:
        ecr_prime = eu
    else:
        ecr_prime = expression_ecr

    # Calculate Ultimate Stress of Steel (fu)
    if fu == 0:
        if fy <= 400:
            fu = (1.6 - (0.002 * (fy - 200)))* fy
        elif fy <= 800:
            fu = (1.2 - (0.000375 * (fy - 400)))* fy
        elif fy <= 960:
            fu = (1.05 * fy)

    # Calculate Stress (fu_prime)
    expression_fu_prime = fy * (6.8 - (0.013 * CF) - (3.5 / (CF**0.15)) - ((1.3 * (fy**0.25)) * (t_D_fc**0.15)))
    if expression_fu_prime <= fcr_prime:
        fu_prime = fcr_prime + (1 / 1000)
    elif expression_fu_prime > fu:
        fu_prime = fu
    else:
        fu_prime = expression_fu_prime
        
    # Constant value for psi
    psi = 1.5
    
    # Calculate Strain Hardening Exponent (p)
    p = Ep * ((eu - ecr_prime)/(fu_prime - fcr_prime))
    
    # Output dictionary with calculated steel parameters
    output = {
        'Modulus of Elasticity of Steel': Es,
        'Strain Corresponding to First Peak Stress': epsilony_prime,
        'First Peak Stress': fy_prime,
        'Critical Stress': fcr_prime,
        'Calculate Ultimate Strain': eu,
        'Critical Strain': ecr_prime,
        'Ultimate Stress of Steel': fu,
        'Stress': fu_prime,
        'Initial Modulus of Elasticity': Ep,
        'Strain Hardening Exponent': p,
        'Strain at Peak Stress': epsilon_c0,
        'Strain Softening Exponent': psi
    }
    
    return output

# Calculate steel parameters based on user input
result = calculate_steel_parameters(parameters, A_s, A_total, A_cc, parameters['Es'])

# Print steel parameters
print("\nSteel Parameters:")
for key, value in result.items():
    print(f"{key}: {value}")

# Function to calculate concrete parameters
def calculate_concrete_parameters(parameters, A_cc, A_s, eu=1.0):
    # Extract necessary parameters
    fc = parameters['fc']
    D = parameters['D']
    t = parameters['t']
    eu = result['Calculate Ultimate Strain']
    fy = parameters['fy']
        
    # Calculate Modulus of elasticity of concrete (Ec)
    if parameters['Ec'] == 0:
        Ec = 4700 * math.sqrt(fc)  # Calculating Ec based on the provided formula
    else:
        Ec = parameters['Ec']
    
    # Calculate Confinement Factor (CF)
    CF = (A_s * fy) / (fc * A_cc)
    
    # Calculate various concrete parameters
    ratio1 = (parameters['fy'] / fc) ** 0.696
    ratio2 = (D / t) ** 0.46
    if (1 + 0.2 * ratio1 + (0.9 - 0.25 * ratio2) * math.sqrt(CF)) < 1:
        fcc_prime = fc
    elif (1 + 0.2 * ratio1 + (0.9 - 0.25 * ratio2) * math.sqrt(CF)) > 3:
        fcc_prime = 3 * fc
    else:
        fcc_prime = (1 + 0.2 * ratio1 + (0.9 - 0.25 * ratio2) * math.sqrt(CF)) * fc
    
    # Check condition for epsilon_cc_prime
    condition_value = 3000 - (10.4 * (parameters['fy'] ** 1.4) * (fcc_prime ** -1.2) * (0.73 - 3785.8 * ((D / t) ** -1.5)))/ 1000000
    if condition_value < fcc_prime:
        epsilon_cc_prime = condition_value
    else:
        epsilon_cc_prime = fcc_prime 
    
    # Calculate parameter A
    A = (1 + (0.25 * (CF ** (0.05 + (0.25 / CF))) * (epsilon_cc_prime * Ec))) / fcc_prime
    
    # Calculate parameter B
    expression_B = 2.15 - (2.05 * math.exp(-CF)) - (0.0076 * fc)
    if expression_B < -0.075:
        B = -0.75
    else:
        B = expression_B          
        
    # Calculate parameter fr
    expression = fcc_prime * (3.5 * ((parameters['t'] / (parameters['D'] * (fc ** 0.7))) ** 0.2) - (0.2 / (CF ** 0.3)))
    if expression >= fcc_prime:
        fr = fcc_prime
    else:
        fr = expression
    
    return (Ec, fcc_prime, epsilon_cc_prime, A, B, fr, eu)

# Calculate concrete parameters based on user input
concrete_parameters = calculate_concrete_parameters(parameters, A_cc, A_s, eu=result['Calculate Ultimate Strain'])

# Print concrete parameters
print("\nConcrete Parameters:")
for param, value in zip(['Ec', 'fcc_prime', 'epsilon_cc_prime', 'A', 'B', 'fr', 'eu'], concrete_parameters):
    print(f"{param}: {value}")

# Function to calculate stress based on given parameters and strain
def calculate_sigma(strain, parameters, A_s, A_total, A_cc):
    # Calculate steel parameters
    steel_params = calculate_steel_parameters(parameters, A_s, A_total, A_cc, parameters['Es'])
    
    # Extract necessary parameters from steel_params dictionary
    epsilony_prime = steel_params['Strain Corresponding to First Peak Stress']
    Es = steel_params['Modulus of Elasticity of Steel']
    fy_prime = steel_params['First Peak Stress']
    fcr_prime = steel_params['Critical Stress']
    psi = steel_params['Strain Softening Exponent']
    eu = steel_params['Calculate Ultimate Strain']
    fu_prime = steel_params['Ultimate Stress of Steel']
    ecr_prime = steel_params['Critical Strain']
    p = steel_params['Strain Hardening Exponent']
    
    # Calculate stress based on given conditions
    if length_outer_diameter_ratio > 5:
        return 0
    elif strain < epsilony_prime:
        return Es * strain
    elif epsilony_prime <= strain <= ecr_prime:
        return fcr_prime - (fcr_prime - fy_prime) * ((ecr_prime - strain) / (ecr_prime - epsilony_prime)) ** psi
    elif ecr_prime < strain <= eu:
        return fu_prime - (fu_prime - fcr_prime) * ((eu - strain) / (eu - ecr_prime)) ** p
    elif strain > eu:
        return fu_prime

# Function to read parameters from JSON file
def read_parameters():
    with open("parameters.json", "r") as f:
        parameters = json.load(f)
    return parameters

# Function to calculate stress from CSV file
# Function to calculate stress from CSV file
def calculate_stress_from_csv(csv_filename):
    # Check if the CSV file exists
    if not os.path.exists(csv_filename):
        print(f"Error: File '{csv_filename}' not found.")
        return [], []

    # Read parameters from JSON file
    parameters = read_parameters()

    # Calculate parameters
    A_s, A_total, A_cc, CF, outer_diameter_thickness_ratio, length_outer_diameter_ratio = calculate_parameters(parameters)

    # Read strain values from CSV file
    strain_values = []
    with open(csv_filename, 'r', encoding='utf-8-sig') as file:  # Open with utf-8-sig encoding to ignore BOM
        reader = csv.reader(file)
        next(reader)  # Skip header row if it exists
        for row in reader:
            try:
                strain_values.append(float(row[0]))
            except ValueError:
                print(f"Warning: Could not convert '{row[0]}' to float. Skipping.")
                continue
            
    # Calculate stress for each strain value
    stresses = []
    for strain in strain_values:
        stress = calculate_sigma(strain, parameters, A_s, A_total, A_cc, length_outer_diameter_ratio)
        if stress is not None:
            stresses.append(stress)
        else:
            stresses.append(None)
    return strain_values, stresses

# Example usage
csv_filename = 'D:\\New Research\\strain_value.csv'
strain_values, stresses = calculate_stress_from_csv(csv_filename)
for strain, stress in zip(strain_values, stresses):
    if stress is not None:
        print(f"For strain value {strain}, stress is: {stress:.6f}")
    else:
        print(f"Invalid input for strain value {strain}. Please check the parameters.")
        
# Plot stress-strain curve
plt.figure(figsize=(10, 6))
plt.plot(strain_values, stresses, marker='o', linestyle='-')
plt.title('Stress-Strain Curve')
plt.xlabel('Strain')
plt.ylabel('Stress')
plt.grid(True)
plt.show()

# Create GUI
root = tk.Tk()
root.title("Steel Stress-Strain Calculator")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Labels and Entry widgets for parameters
tk.Label(frame, text="D (outer diameter of steel tube):").grid(row=0, column=0, sticky="w")
entry_D = tk.Entry(frame)
entry_D.grid(row=0, column=1)

tk.Label(frame, text="t (thickness of steel tube):").grid(row=1, column=0, sticky="w")
entry_t = tk.Entry(frame)
entry_t.grid(row=1, column=1)

tk.Label(frame, text="fc (unconfined concrete strength):").grid(row=2, column=0, sticky="w")
entry_fc = tk.Entry(frame)
entry_fc.grid(row=2, column=1)

tk.Label(frame, text="Ec (Modulus of elasticity of concrete):").grid(row=3, column=0, sticky="w")
entry_Ec = tk.Entry(frame)
entry_Ec.grid(row=3, column=1)

tk.Label(frame, text="fy (yield stress of steel):").grid(row=4, column=0, sticky="w")
entry_fy = tk.Entry(frame)
entry_fy.grid(row=4, column=1)

tk.Label(frame, text="fu (ultimate stress of steel):").grid(row=5, column=0, sticky="w")
entry_fu = tk.Entry(frame)
entry_fu.grid(row=5, column=1)

tk.Label(frame, text="Es (modulus of elasticity of steel):").grid(row=6, column=0, sticky="w")
entry_Es = tk.Entry(frame)
entry_Es.grid(row=6, column=1)

tk.Label(frame, text="L (length of column):").grid(row=7, column=0, sticky="w")
entry_L = tk.Entry(frame)
entry_L.grid(row=7, column=1)

# Button to calculate stress-strain curve
button_calculate = tk.Button(frame, text="Calculate Stress-Strain Curve", command=lambda: calculate_stress_from_csv("D:\\New Research\\strain_value.csv"))
button_calculate.grid(row=8, columnspan=2)

root.mainloop()
