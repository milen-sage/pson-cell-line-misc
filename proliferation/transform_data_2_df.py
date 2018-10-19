import pandas as pd
import json
import sys, os
import re
sys.path.append(os.path.abspath('..'))
from cell_line_2_catalog_map_extract import to_id 
import itertools as it
if __name__ == "__main__":
    
    cell_line_proliferation_xls = pd.ExcelFile("Leidos_project_counting_results.xlsx")

    cell_lines = cell_line_proliferation_xls.sheet_names

    # will construct a new data frame "manually" because it is easier to get a good layout that way (compared to useing pandas transforms)
    cell_line_proliferation_df = "cl_id,condition_id,plate,trial,single,touching,total,frame_num\n"

    cell_line_dfs = pd.DataFrame()
    for cell_line in cell_lines:
        
        cell_line_df = pd.read_excel("Leidos_project_counting_results.xlsx", sheet_name = cell_line)

        # cleaning column names
        cell_line_df.rename(to_id, axis = "columns", inplace = True)
        
        new_column_names = {}
        old_column_names = cell_line_df.columns
        for i, col in enumerate(old_column_names):
            if "frame" in col:
                new_column_names[col] = re.search("t.p.", old_column_names[i-1]).group(0) + re.search("\#frames", col).group(0)
        cell_line_df.rename(columns = new_column_names, inplace = True)

        cell_line_df["cl_id"] = pd.Series([to_id(cell_line)]*len(cell_line_df.index))
        cell_line_df["condition_id"] = cell_line_df["condition"].apply(to_id)


        #store condition ids to full name and vice versa maps (usefuk to link w/ other datasets)
        condition_id_2_full = dict(zip(cell_line_df["condition_id"], cell_line_df["condition"]))
        condition_full_2_id = dict(zip(cell_line_df["condition_id"], cell_line_df["condition"]))
        
        with open("condition_id_2_full.json", "w") as c_f:
            json.dump(condition_id_2_full, c_f, indent = 3)
 
        with open("condition_full_2_id.json", "w") as c_f:
            json.dump(condition_full_2_id, c_f, indent = 3)

        # no need to keep that column anymoe so drop it
        cell_line_df.drop(["condition"], axis = 1, inplace = True)
    

        # generating plates and trial combinations for each cell line and each condition and storing corresponding values in each row
        for idx, row in cell_line_df.iterrows():

            for combo in it.product([1, 2], [1, 2, 3]):

                cell_line_proliferation_df += to_id(cell_line) + ","
                cell_line_proliferation_df += to_id(row["condition_id"]) + ","

                plate = str(combo[0])
                trial = str(combo[1])
                trial_plate_combo = "t" + trial + "p" + plate
                
                if(trial_plate_combo + "single" in row):
                    single = str(row[trial_plate_combo + "single"]) 
                else:
                    single = "NA"
                
                if(trial_plate_combo + "touching" in row):
                    touching = str(row[trial_plate_combo + "touching"]) 
                else:
                    touching = "NA"
                
                if(trial_plate_combo + "total" in row):
                    total= str(row[trial_plate_combo + "total"]) 
                else:
                    total = "NA"

                if(trial_plate_combo + "#frames" in row):
                    frame_num =str(row[trial_plate_combo + "#frames"])
                    #print(trial_plate_combo + "#frames")
                    #print(row["condition_id"])
                    #print(type(row[trial_plate_combo + "#frames"]))
                    #print(row[trial_plate_combo + "#frames"])
                else:
                    frame_num = "NA"

                cell_line_proliferation_df += plate + ","
                cell_line_proliferation_df += trial + ","
                cell_line_proliferation_df += single + ","
                cell_line_proliferation_df += touching + ","
                cell_line_proliferation_df += total + ","
                cell_line_proliferation_df += frame_num + "\n"
     
    with open("cell_line_proliferation.csv", "w") as cp_f:
        cp_f.write(cell_line_proliferation_df)


    # clean supplemental data for plate trial count timing (hours from start of experiment)
    counting_times_df = pd.read_excel("Cell_counting_times.xlsx")

    counting_times_df.rename(columns = {"Cell line":"cl_id"}, inplace = True)
    counting_times_df["cl_id"] = counting_times_df["cl_id"].apply(to_id)

    counting_times_df.to_csv("cell_line_proliferation_counting_times.csv", index = False)
