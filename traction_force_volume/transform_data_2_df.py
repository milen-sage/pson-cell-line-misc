import pandas as pd
import json
import glob
import re
import numpy as np
import difflib
import sys, os
sys.path.append(os.path.abspath("../"))
from cell_line_2_catalog_map_extract import to_id


def match_id(string, dict_file, err_string = ""):
    with open(dict_file, "r") as c_f:
        match_ids = json.load(c_f).keys()

    # can get more sophisticated in matching here but this works for this dataset    
    match = difflib.get_close_matches(string, match_ids, n = 1)
    
    if not match:
        print("COULDN'T MATCH " + string)
        print("ERROR: " + err_string) if err_string else print("")
        return ""

    return match[0]


if __name__ == "__main__":
   

    # reading all excel files (one per cell line)
    cell_line_traction_force_volume_files = [glob.glob("./raw/*.xlsx")][0]
    
    # each file has 4 spread sheets we need to parse        
    spread_sheet_names = ["Cell Volume", "Traction Force", "Nuclear Volme", "Cell Area"]

    # preparing a csv to contain the newly extracted data
    traction_force_volume_dfs = [] 

    for cell_line_traction_force_volume_file in cell_line_traction_force_volume_files:

        # getting cell line id from file name
        cl_id = match_id(to_id(os.path.basename(cell_line_traction_force_volume_file).split(".xlsx")[0]), dict_file = "../cell_line_strp_2_full.json", err_string = cell_line_traction_force_volume_file)
        if not cl_id:
            continue

        excel_spreads = pd.ExcelFile(cell_line_traction_force_volume_file)

        # getting different physical measurements from each sheet (per condition)

        traction_force_volume_df = pd.DataFrame()
        for sheet in spread_sheet_names:
           
            measurements_df = pd.read_excel(excel_spreads, sheet_name = sheet)
             
            condition = measurements_df.columns[0]

            condition_id = match_id(to_id(condition), dict_file = "../condition_id_2_full.json", err_string = cell_line_traction_force_volume_file + "::" + sheet + " :: " + condition)  

            if not "condition_id" in traction_force_volume_df.columns:
                traction_force_volume_df["condition_id"] = len(measurements_df.index)*[condition_id]

            traction_force_volume_df[sheet] = measurements_df[condition]

        traction_force_volume_df["cl_id"] = len(traction_force_volume_df.index)*[cl_id]

        traction_force_volume_dfs.append(traction_force_volume_df)

    traction_force_volume_df = pd.concat(traction_force_volume_dfs)

    # renaming columsn to avoid typos and be more consistent
    column_map = dict(zip(traction_force_volume_df.columns, ["condition_id", "cell_volume", "traction_force", "nuclear_volume", "cell_area", "cl_id"]))
    traction_force_volume_df = traction_force_volume_df.rename(columns = column_map)
    
    traction_force_volume_df.to_csv("traction_force_volume.csv", index = False)
