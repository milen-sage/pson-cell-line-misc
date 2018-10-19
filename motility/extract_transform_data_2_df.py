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
   
    raw_motility_dfs = []
    summary_motility_dfs = []

    motility_columns = ["avg_end_to_end_dist", "avg_total_distance", "avg_speed", "end_to_end_dist_st_dev", "total_distance_st_dev", "speed_st_dev", "end_to_end_dist_st_err", "total_distance_st_err", "speed_st_err", "num_cells"]

    for cell_line_cat_num in next(os.walk("."))[1]:
        
        trials_raw = [glob.glob("./" + cell_line_cat_num + "/**/*.txt", recursive = True)][0]
        raw_motility_data_columns = ["id","track", "slice", "x", "y", "distance", "velocity", "pixel_value"]

        for trial_raw in trials_raw:
            trial_raw_toks = trial_raw.split("/")
            
            cl_condition = trial_raw_toks[2] 
            cl_condition_toks = cl_condition.split("_")

            cl_id = match_id(to_id(cl_condition_toks[0]), dict_file = "../cell_line_strp_2_full.json", err_string = cl_condition)
            condition_id = match_id(to_id("".join(cl_condition_toks[1:])), dict_file = "../condition_id_2_full.json", err_string = cell_line_cat_num + "::" + cl_condition)

            position_plate_trial = trial_raw_toks[3].replace(".txt", "")
            
            position_plate_trial_toks = [tok for tok in position_plate_trial.split("_") if not tok == ""]
            
            plate = ""
            position = ""
            trial = ""
            
            if "Results" in position_plate_trial:
                if "pos" in position_plate_trial and position_plate_trial[-1] == "_": # pattern ex: Results_from_pos41_in_um_per_sec__5_.txt
                    print(position_plate_trial)
                    
                    plate = re.search("p\d", position_plate_trial)
                    if not plate:
                        plate = 1 #if plate is not recorded then this is experiment from plate 1
                    else:
                        plate = plate.group(0)
                        plate = int(plate[-1]) + 1 # given this pattern of results file name, first plate is not denoted with p; hence we add 1 to the plate numbers denoted with p

                    position = int(position_plate_trial_toks[2][3:])
                    trial = int(position_plate_trial_toks[-1])
                    if trial == "":
                        trial = 1

                elif "pos" in position_plate_trial and position_plate_trial[-1] != "_": # pattern ex: Results_from_HT29_p1_pos9 or Results_from_htert_hpne_p2_pos_15 or Results_from_pos4_in_um_per_sec_p1, etc.
                    print(position_plate_trial)
                    plate = re.search("p\d", position_plate_trial)
                    if not plate:
                        plate = 1 #if plate is not recorded then this is experiment from plate 1
                    else:
                        plate = plate.group(0)
                        plate = int(plate[-1])

                    for token in position_plate_trial_toks:
                        position = re.search("pos\d", token)
                        if position:
                            position = int(token[3:])
                            break
                        else:
                            position = re.search("pos_\d{1,2}", position_plate_trial)
                            if position:
                                position = int(position.group(0).split("_")[1])
 
                        trial = 1

                elif position_plate_trial[-1] == "_": # pattern ex: Results_from_31_p2__1_.txt 
                    print(position_plate_trial)
                    plate = re.search("p\d", position_plate_trial)
                    if not plate:
                        plate = 1 #if plate is not recorded then this is experiment from plate 1
                    else:
                        plate = plate.group(0)
                        plate = int(plate[-1])

                    position = position_plate_trial_toks[2]
                    if "pos" in position:
                        position = int(position[2:])
                    
                    trial = int(position_plate_trial_toks[-1])

                #Results_from_11_p1__6_500PAA_FN.txt
                else:  #pattern ex: Results_from_22RV1_p3_glass.txt      
                    print(position_plate_trial)
                    plate =  re.search("p\d", position_plate_trial).group(0)
                    plate = int(plate[-1])

                    # look up the position based on a match between condition and position codes
                    condition = "".join(re.split("p\d", position_plate_trial)[1][1:].split("_")) 
                    condition = match_id(to_id(condition), dict_file = "./condition_id_2_position.json", err_string = position_plate_trial)
                    
                    with open("./condition_id_2_position.json") as c_f:
                        cond_2_pos = json.load(c_f)

                    position = int(cond_2_pos[condition])
                    
                    trial = 1
            
            end2end_dist = ""
            tot_dist = ""
            speed = ""

            if "summary" in position_plate_trial:
                summary_motility_df = pd.read_csv(trial_raw, delimiter = "\t")
                
                # collecting all summary data can be done in a more concise way; but this works for now
                motility_data = summary_motility_df[0:1].values[0] # average 
                motility_data = np.append(motility_data, summary_motility_df[2:3].values[0]) # st deviation
                motility_data = np.append(motility_data, summary_motility_df[3:4].values[0]) # st err
                motility_data = np.append(motility_data, np.array(summary_motility_df[1:2].iloc[0,0])) # cell number (same for all measured variables)
                summary_motility_reshaped_df = pd.DataFrame.from_dict({0:motility_data}, orient = "index", columns = motility_columns)
                
                summary_motility_reshaped_df["cl_id"] =  len(summary_motility_reshaped_df.index)*[cl_id]
                summary_motility_reshaped_df["condition_id"] =  len(summary_motility_reshaped_df.index)*[condition_id]

                # clean null data
                summary_motility_reshaped_df = summary_motility_reshaped_df.dropna(how = "any")

                summary_motility_dfs.append(summary_motility_reshaped_df)
 
            motility_measurement_id = cl_id + "_" + condition_id + "_" + str(position) + "_" + str(plate) + "_" + str(trial)
            raw_data_path = os.path.relpath(trial_raw)

            if "Results" in position_plate_trial:
                try:
                    raw_motility_df = pd.read_csv(trial_raw, delimiter = '\t', encoding = "ISO-8859-1") # change encoding to account for non-standard chars in column names
                except UnicodeDecodeError:
                    print("Decoding error in " + trial_raw)
                    continue
                
                columns_map = dict(zip(raw_motility_df.columns, raw_motility_data_columns))
                
                raw_motility_df.rename(columns = columns_map, inplace = True)
                raw_motility_df["motility_measurement_id"] = len(raw_motility_df.index)*[motility_measurement_id]
                raw_motility_df["cl_id"] = len(raw_motility_df.index)*[cl_id]
                raw_motility_df["condition_id"] = len(raw_motility_df.index)*[condition_id]
                raw_motility_df["raw_data_path"] = len(raw_motility_df.index)*[raw_data_path]

                raw_motility_dfs.append(raw_motility_df)


    raw_motility_df = pd.concat(raw_motility_dfs)
    raw_motility_df.drop(["1 frame/10 min",	"100 pixel/frame ", "100 um/149 pixel", "Unnamed: 10", "Unnamed: 8","Unnamed: 9"], errors = "ignore", inplace = True, axis = 1)
    raw_motility_df.to_csv("raw_motility_data.csv", index = False)

    summary_motility_df = pd.concat(summary_motility_dfs)
    summary_motility_df.to_csv("summary_motility_data.csv", index = False)
