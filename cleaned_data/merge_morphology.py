import pandas as pd

aspect_ratio_df = pd.read_csv("./cell_line_aspect_ratio.csv").sort_values(["cl_id", "condition_id"])
circularity_df = pd.read_csv("./cell_line_circularity.csv").sort_values(["cl_id", "condition_id"])
area_df = pd.read_csv("./cell_line_area.csv").sort_values(["cl_id", "condition_id"])

morphology_df = pd.DataFrame(index = aspect_ratio_df.index, columns = ["condition_id", "cl_id", "aspect_ratio", "area", "circularity"])
morphology_df["condition_id"] = aspect_ratio_df.as_matrix(columns = ["condition_id"])
morphology_df["cl_id"] = aspect_ratio_df.as_matrix(columns = ["cl_id"])
morphology_df["aspect_ratio"] = aspect_ratio_df.as_matrix(columns = ["aspect_ratio"])
morphology_df["area"] = area_df.as_matrix(columns = ["area"])
morphology_df["circularity"] = circularity_df.as_matrix(columns = ["circularity"])

print(morphology_df.head(100))
print(morphology_df.describe())

morphology_df.to_csv("cell_line_morphology.csv", index = False)
