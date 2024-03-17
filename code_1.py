import json
import math
import csv
import os
import matplotlib.pyplot as plt

def get_parameters():
    parameters = {}
    parameters['D'] = float(input("Enter outer diameter of steel tube (D): "))
    parameters['t'] = float(input("Enter thickness of steel tube (t): "))
    
    while True:
        fc = float(input("Enter unconfined concrete strength (fc): "))
        if 15 <= fc <= 200:
            parameters['fc'] = fc
            break
        else:
            print("Unconfined concrete strength (fc) must be between 15 and 200. Please enter a valid value.")
            
    parameters['Ec'] = float(input("Enter the Modulus of elasticity of concrete (Ec):"))

    while True:
        fy = float(input("Enter yield stress of steel (fy): "))
        if fy < 960:
            parameters['fy'] = fy
            break
        else:
            print("Yield stress of steel (fy) must be less than 960. Please enter a valid value.")
    
    parameters['fu'] = float(input("Enter ultimate stress of steel (fu): "))
    parameters['Es'] = float(input("Enter modulus of elasticity of steel (Es): "))
    
    while True:
        parameters['L'] = float(input("Enter length of column (L): "))
        if parameters['L'] / parameters['D'] <= 5:
            break
        else:
            print("Warning: Length/Outer diameter ratio should be less than or equal to 5. Please enter a valid value.")
    
    # Save parameters to a JSON file
    save_parameters(parameters)

    return parameters

def save_parameters(parameters):
    with open("parameters.json", "w") as f:
        json.dump(parameters, f)

def calculate_parameters(parameters):
    D = parameters['D']
    t = parameters['t']
    L = parameters['L']
    Es = parameters['Es']
    fc = parameters['fc']
    Ec = parameters['Ec']
    fy = parameters['fy']
    fu = parameters['fu']
            
    # Outer diameter/thickness ratio
    outer_diameter_thickness_ratio = D / t

    # Length/outer diameter ratio
    length_outer_diameter_ratio = L / D

    # Cross section area of core concrete
    A_cc = math.pi * (D - 2 * t)**2 / 4
    
    # Total cross section area of column
    A_total = math.pi * D**2 / 4

    # Cross section area of steel
    A_s = A_total - A_cc
    
    # Confinement factor
    CF = (A_s * fy) / (fc * A_cc)

    return A_s, A_total, A_cc, CF, outer_diameter_thickness_ratio, length_outer_diameter_ratio

# Get parameters
parameters = get_parameters()
print("Parameters saved to parameters.json file.")

# Calculate parameters
A_s, A_total, A_cc, CF, outer_diameter_thickness_ratio, length_outer_diameter_ratio = calculate_parameters(parameters)

# Print parameters
print("Parameters:")
print(f"CSA of Steel: {A_s}")
print(f"Total CSA of Column: {A_total}")
print(f"CSA of Concrete: {A_cc}")
print(f"Confinement Factor: {CF}")
print(f"Outer Diameter to Thickness Ratio: {outer_diameter_thickness_ratio}")
print(f"Length to Outer Diameter Ratio: {length_outer_diameter_ratio}")

def calculate_steel_parameters(parameters, A_s, A_total, A_cc, Es):
    fy = parameters['fy']
    fu = parameters['fu']
    fc = parameters['fc']
    epsilon_c0 = parameters.get('epsilon_c0', 0)  # Default value for epsilon_c0
    Ec = parameters['Ec']
    CF = (A_s * fy) / (fc * A_cc)
    
    # Calculate Initial Modulus of Elasticity (Ep)
    Ep = 0.02 * parameters['Es']
    
    if parameters['Ec'] == 0:
        Ec = 4700 * math.sqrt(fc)  # Calculating Ec based on the provided formula
    else:
        Ec = parameters['Ec']
    
    # Calculate Normal Strain of Steel
    epsilon_y = fy / Es
         
    # Calculate Strain at Peak Stress (epsilon_c0)
    epsilon_c0 = 0.002 * (1 + A_s / A_total * Es / Ec)  
    
    #Calculate First Peak Stress (fy_prime)    
    expression = 1.02 - 0.01 * ((epsilon_y / epsilon_c0) ** 1.5) * ((parameters['D'] / parameters['t']) ** 0.5)
    
    if expression < 0:
        fy_prime = 0.001 * fy
    elif expression > 1:
        fy_prime = fy
    else:
        fy_prime = expression * fy
        
    # Calculate Strain Corresponding to First Peak Stress (ey_prime)
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
        
    # Calculate Strain Softening Exponent (psi)
    psi = 1.5  # Constant value for psi
    
        
    # Calculate Strain Hardening Exponent (p)
    p = Ep * ((eu - ecr_prime)/(fu_prime - fcr_prime))
    
   
    
    # Output dictionary with labels
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


result = calculate_steel_parameters(parameters, A_s, A_total, A_cc, parameters['Es'])

# Print steel parameters
print("\nSteel Parameters:")
for key, value in result.items():
    print(f"{key}: {value}")

def calculate_concrete_parameters(parameters, A_cc, A_s, eu=1.0):
    
    fc = parameters['fc']
    D = parameters['D']
    t = parameters['t']
    eu = result['Calculate Ultimate Strain']
    fy = parameters['fy']
        
    if parameters['Ec'] == 0:
        Ec = 4700 * math.sqrt(fc)  # Calculating Ec based on the provided formula
    else:
        Ec = parameters['Ec']
    
    CF = (A_s * fy) / (fc * A_cc)
    
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
    
    A = (1 + (0.25 * (CF ** (0.05 + (0.25 / CF))) * (epsilon_cc_prime * Ec))) / fcc_prime
    
    expression_B = 2.15 - (2.05 * math.exp(-CF)) - (0.0076 * fc)
    if expression_B < -0.075:
        B = -0.75
    else:
        B = expression_B          
        
    expression = fcc_prime * (3.5 * ((parameters['t'] / (parameters['D'] * (fc ** 0.7))) ** 0.2) - (0.2 / (CF ** 0.3)))
    if expression >= fcc_prime:
        fr = fcc_prime
    else:
        fr = expression
    
    return (Ec, fcc_prime, epsilon_cc_prime, A, B, fr, eu)

# Calculate concrete parameters
concrete_parameters = calculate_concrete_parameters(parameters, A_cc, A_s, eu=result['Calculate Ultimate Strain'])

# Print concrete parameters
print("\nConcrete Parameters:")
for param, value in zip(['Ec', 'fcc_prime', 'epsilon_cc_prime', 'A', 'B', 'fr', 'eu'], concrete_parameters):
    print(f"{param}: {value}")

# Function to calculate stress based on given parameters and strain
def calculate_sigma(strain, parameters, A_s, A_total, A_cc):
    # Calculate steel parameters
    steel_params = calculate_steel_parameters(parameters, A_s, A_total, A_cc, parameters['Es'])
    
    # Obtain values from steel_params dictionary
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
        stress = calculate_sigma(strain, parameters, A_s, A_total, A_cc)
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
plt.title('Steel Stress-Strain Curve')
plt.xlabel('Strain')
plt.ylabel('Stress')
plt.grid(True)
plt.show()
