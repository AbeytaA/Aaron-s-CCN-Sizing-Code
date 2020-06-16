# Aaron Abeyta
# Main File
# Currently going to attempt to have Python Run CEA

import subprocess
import math
import numpy 
import pandas as pd
from math import sqrt
import csv


def user_inputs():
    Pc = float(input("Desired Pressure:"))
    Pc_unit = str(input("Units for Pressure (Mpa, bar, psia):"))
    fuel = str(input("Fuel type, you can also do custom:"))
    oxidizer
    # o/f range or phi range
    # Pressure ratio (define this for nooobz)
    # infinite combustion / finite combustion
    # other potential CEA inputs


def run_cea(input_name):

    cea = subprocess.Popen('FCEA2m.exe', stdin=subprocess.PIPE,stdout=subprocess.PIPE, universal_newlines=True)
    cea.communicate(input_name + "\n")


def parse_cea(filename):
    """
    Parses CEA's output csv and stores optimal values in a dictionary
    """

    df = pd.read_csv(filename)
    cea_dict = {}

    isp_idx = df['isp         '].idxmax()

    cea_dict['chamber pressure'] = df['p           '].loc[isp_idx - 2] * 100000
    cea_dict['optimal of'] = df['o/f         '].loc[isp_idx]
    cea_dict['optimal mw'] = df['mw          '].loc[isp_idx - 2]
    cea_dict['optimal temperature'] = df['t           '].loc[isp_idx - 2]
    cea_dict['optimal gamma'] = df['gam         '].loc[isp_idx - 2]
    cea_dict['optimal mach number'] = df['mach        '].loc[isp_idx]
    
    return cea_dict


def calculate_nozzle_params(filename, thrust):

    cea_dict = parse_cea(filename)

    Pc = cea_dict['chamber pressure']
    of = cea_dict['optimal of']
    mw = cea_dict['optimal mw']
    Tc = cea_dict['optimal temperature']
    gam = cea_dict['optimal gamma']
    Me = cea_dict['optimal mach number']

    thrust = thrust/0.224809
    Ru = 8.3145 

    R = Ru / (mw / 1000) 

    ve = sqrt(2 * gam / (gam - 1) * R * Tc * (1 - (1 / 56.12) ** ((gam - 1) / gam) ) )

    mdot = thrust / ve 

    At = (mdot * sqrt(gam * R * Tc)) / (Pc * gam) * 1 / (sqrt((2/(gam + 1) ** ((gam + 1)/(gam - 1)))))

    Ae = At * sqrt(1 / (Me ** 2) * (2 / (gam + 1) * ((1 + (gam - 1) / 2 * Me ** 2) ** ((gam + 1)/(gam - 1)))))

    AR = Ae / At

    mdotf = mdot / (1 + of)

    mdoto = mdot - mdotf

    cea_dict['Exhaust velocity (m/s)'] = ve 
    cea_dict['total mass flow'] = mdot
    cea_dict['fuel mass flow'] = mdotf
    cea_dict['ox mass flow'] = mdoto
    cea_dict['Throat Area'] = At
    cea_dict['Exit Area'] = Ae
    cea_dict['Area Ratio'] = AR 

    title_columns = ['Parameter', 'Value']
    out_name = filename.split('.')
    out_name = out_name[0] + '_out.csv' 
    
    
    with open(out_name, 'w') as out_name:
        writer = csv.writer(out_name)
    
        for key, value in cea_dict.items():
            writer.writerow([key, value])

def main():
    input_str = "denateth75_nitrous_700_2"
    run_cea(input_str)
    calculate_nozzle_params(input_str + ".csv", 1200)


if __name__ == "__main__":
    main()