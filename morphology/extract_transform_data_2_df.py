import pandas as pd
import json
import glob
import re
import difflib
import sys, os
sys.path.append(os.path.abspath("../"))
from cell_line_2_catalog_map_extract import to_id

def match_id(row):
    with open("../condition_id_2_full.json", "r") as c_f:
        condition_ids = json.load(c_f).keys()

    # can get more sophisticated in matching here but this works for this dataset    
    match = difflib.get_close_matches(row["condition_id"], condition_ids, n = 1)
    
    if not match:
        print(row["condition_id"])
        return row["condition_id"]

    return match[0]

if __name__ == "__main__":

    morphology_properties = ["area", "aspect_ratio", "circularity"]

    for morph_prop in morphology_properties:

        # get all files for that morphology properties
        morph_cell_lines = glob.glob("./original_txts/*" + morph_prop + "*.txt")
        
        morphology_df = pd.DataFrame()
        for morph_cell_line in morph_cell_lines:
            # extract cell line id
            cl_id = to_id(morph_cell_line.split("_" + morph_prop)[0]).replace("./originaltxts/", "")    
            cell_line_morph_df = pd.read_csv(morph_cell_line, delimiter = "\t")

            # clean exrtraneous columns introduced by pandas csv parser
            if "Unnamed: 7" in cell_line_morph_df.columns:
                cell_line_morph_df.drop(["Unnamed: 7"], axis = 1, inplace = True)
            
            # getting condition as a column for which each cell's morphology properties is measured
            cell_line_morph_df = cell_line_morph_df.transpose().stack().reset_index()
            cell_line_morph_df.drop(["level_1"], inplace = True, axis = 1)
            cell_line_morph_df.rename(columns = {0:morph_prop, "level_0":"condition_id"}, inplace = True)
            
            # converting condition string to condition id
            cell_line_morph_df["condition_id"] = cell_line_morph_df["condition_id"].apply(to_id)

            # finding match in existing IDs from other datasets
            cell_line_morph_df["condition_id"] = cell_line_morph_df.apply(match_id, axis = 1)

            # adding cell line ids
            cell_line_morph_df["cl_id"] = pd.Series([cl_id]*len(cell_line_morph_df.index))
        
            if morphology_df.empty:
                morphology_df = cell_line_morph_df
            else:
                morphology_df = pd.concat([morphology_df, cell_line_morph_df])                        

        print(morphology_df.describe())
        morphology_df.to_csv("cell_line_" + morph_prop + ".csv", index = False) 

