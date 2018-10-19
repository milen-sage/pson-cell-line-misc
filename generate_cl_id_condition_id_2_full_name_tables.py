import pandas as pd
import json

with open("./condition_id_2_full.json", "r") as cd_f:
    condition_id_2_full = json.load(cd_f)

with open("./cell_line_strp_2_full.json", "r") as cl_f:
    cl_id_2_full = json.load(cl_f)

cell_lines_df = pd.DataFrame.from_dict({"cl_id":list(cl_id_2_full.keys()), "cell_line":list(cl_id_2_full.values())})

conditions_df = pd.DataFrame.from_dict({"condition_id":list(condition_id_2_full.keys()), "condition":list(condition_id_2_full.values())})

cell_lines_df.to_csv("cell_lines.csv")
conditions_df.to_csv("conditions.csv")
