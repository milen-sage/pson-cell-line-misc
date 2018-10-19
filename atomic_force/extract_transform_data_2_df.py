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
   

    # we will construct a new dataframe since the data is scattered across multiple spreadsheets and textfiles that need to be cleaned and munged
    atomic_force_df = "cl_id,condition_id,atomic_force_measurement_id,date,young_modulus,spring_constant\n"
    
    raw_atomic_force_dfs = []
    for cell_line_cat_num in next(os.walk("."))[1]:
        
        trials_raw = [glob.glob("./" + cell_line_cat_num + "/ASCII_for_upload/**/*.txt", recursive = True)][0]
        
        # go over raw force files extract data and get corresponding Young's modulus
        for trial_raw in trials_raw:
           
            # some files have multiple errors (e.g. bytes written improperly, multiple unexpected symbols within numbers, etc.
            # since fixing these files would be error-prone and time intensive we just skip them; there are a very small subset of the total
            try:
                raw_force_df = pd.read_csv(trial_raw, delimiter = "\t")
            except (pd.errors.ParserError, UnicodeDecodeError):
                print("FILE HAS ERRORS - SKIPPING" + trial_raw)
                continue

            # getting trial date
            trial_date = os.path.basename(trial_raw).split("cell")[0].split("_")[0:3]
            trial_date = "-".join(trial_date)

            condition_id = ""
            condition_id = os.path.basename(trial_raw).split("cell")[0].split("_")[4:]
            condition_id = match_id(to_id("".join(condition_id).replace(".txt", "").split(".")[0]), "../condition_id_2_full.json")

            if not condition_id:
                # some (small portion) of file names are misconstructed; in those casdes we parse differently to get to the data
                # e.g. 10414_sw_480_ha_coll_1.001.txt instead of 10_4_14_sw_480_ha_coll_1.001.txt
                print("TRYING AGAIN\n")
                condition_id = os.path.basename(trial_raw).split("cell")[0].split("_")[2:]
                condition_id = match_id(to_id("".join(condition_id).replace(".txt", "").split(".")[0]), "../condition_id_2_full.json", err_string = trial_raw + " FAILED MATCH!")

            # get Young's modulus data for this trial's date
            trial_file =  [os.path.basename(t) for t in glob.glob("./" + cell_line_cat_num + "/Analysis_for_upload/" + trial_date.replace("-", "_")+"*")]
            if len(trial_file) > 0:
                trial = trial_file[0] 
            else: 
                print("./" + cell_line_cat_num + "/Analysis_for_upload/" + trial_date.replace("-", "_")+"*")
                trial = None

            # tokenize trial filename
            trial_toks = trial.split("_For_upload")[0].split("_")
 
            # extract Young modulus data frame and pointers to raw data files
            young_modulus_df = pd.read_excel("./" + cell_line_cat_num + "/Analysis_for_upload/" + trial)

            young_modulus_df = young_modulus_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x) 

            # extracting spring constant - a bit hacky since the spring constant is encoded as a column name in the spredsheet along with units and notation....
            spring_constant = re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", young_modulus_df.columns[0]) 
            spring_constant = spring_constant[0] if spring_constant else "NA"
 
            # get Young's modulus for this measurement
            young_modulus_loc = np.where(young_modulus_df.values == os.path.basename(trial_raw).split(".txt")[0])
            if young_modulus_loc[0].size == 0:
                young_modulus = "NA"
                
                print("===================")
                print("COULD NOT FIND Young's modulus")
                print("SEARCHED")
                print(os.path.basename(trial_raw).split(".txt")[0])
                print("AT")
                print("./" + cell_line_cat_num + "/Analysis_for_upload/" + trial)
                print("===================")
                
            else:
                young_modulus = [y[0] for y in young_modulus_loc]
                young_modulus = young_modulus_df.iloc[young_modulus[0], young_modulus[1] + 1]

          
            # getting cell line id
            cl_id = match_id(to_id("".join(trial_toks[3:])), "../cell_line_strp_2_full.json")

            # constructing cell specific, environment specific, cell line specific measurement id
            measurement_id = cl_id + "-" + condition_id + "-" + os.path.basename(trial_raw).split(".txt")[0][-5:]

            atomic_force_df += cl_id + "," + condition_id + "," + measurement_id + "," + trial_date + "," + str(young_modulus) + "," + str(spring_constant) + "\n"
    
            # link raw force measurements per cell, per trial date, per condition to Young modulus calculations via index measurement_id
            raw_force_df["atomic_force_measurement_id"] = len(raw_force_df.index)*[measurement_id]
            
            raw_atomic_force_dfs.append(raw_force_df)

    with open("atomic_force.csv", "w") as a_f:
        a_f.write(atomic_force_df)

    raw_atomic_force_df = pd.concat(raw_atomic_force_dfs)

    raw_atomic_force_df.to_csv("raw_atomic_force.csv", index = False) 
