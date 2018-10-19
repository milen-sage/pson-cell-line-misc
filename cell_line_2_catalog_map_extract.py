import pandas as pd
import json
import re


def replace(string, substitutions):

    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string).lower()

def to_id(string):
    subs = {" ":"", "-":"", ":":"", "_":""}
    return replace(string, subs)

def strip_cell_line_cat_num(row):
    subs = {" ":"", "-":"", ":":"", "_":""}
    return pd.Series([replace(row["catalogNumber"], subs), replace(row["cellLine"], subs)])


if __name__ == "__main__":

    cell_line_cat_num_df = pd.read_csv("cell_line_catalog_numbers_available_data.csv")

    cell_line_cat_num_df = cell_line_cat_num_df[["catalogNumber", "cellLine"]]

    cell_line_cat_num_df[["catalogNumber_strp", "cellLine_strp"]] = cell_line_cat_num_df.apply(strip_cell_line_cat_num, axis = 1)

    cell_line_2_cat_num_map = dict(zip(cell_line_cat_num_df["catalogNumber_strp"], cell_line_cat_num_df["cellLine_strp"]))
    with open("cell_line_2_cat_num.json", "w") as map_f:
        json.dump(cell_line_2_cat_num_map, map_f, indent = 3)

    cat_num_strp_2_full = dict(zip(cell_line_cat_num_df["catalogNumber_strp"], cell_line_cat_num_df["catalogNumber"])) 
    with open("cat_num_strp_2_full.json", "w") as map_f:
        json.dump(cat_num_strp_2_full, map_f, indent = 3)

    cell_line_strp_2_full = dict(zip(cell_line_cat_num_df["cellLine_strp"], cell_line_cat_num_df["cellLine"])) 
    with open("cell_line_strp_2_full.json", "w") as map_f:
        json.dump(cell_line_strp_2_full, map_f, indent = 3)
