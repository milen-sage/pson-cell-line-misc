import synapseclient
from synapseclient import Wiki, File, Project, Folder

import synapseutils
import pandas as pd


def store_table(df, name, proj):

    # creating synapse table schema
    cols = synapseclient.as_table_columns(df)
    schema = synapseclient.Schema(name = name, columns=cols, parent=proj.id)
    schema = syn.store(schema)
    # creating table with schema and df
    table = synapseclient.Table(schema, df)
    # storing table
    table = syn.store(table)



# synapse login
syn = synapseclient.login()

# create project
proj = syn.store(Project(name = "PSON Cell Line Data - Sandbox"))

# read clean data
atomic_force_df = pd.read_csv("./atomic_force.csv")
atomic_force_raw_df = pd.read_csv("./raw_atomic_force.csv")

motility_df = pd.read_csv("./summary_motility_data.csv")
motility_raw_df = pd.read_csv("./raw_motility_data.csv")

traction_force_df = pd.read_csv("./traction_force_volume.csv")

proliferation_df = pd.read_csv("./cell_line_proliferation.csv")
proliferation_samples_timing_df = pd.read_csv("./cell_line_proliferation_counting_times.csv")

area_df = pd.read_csv("./cell_line_area.csv")
circularity_df = pd.read_csv("./cell_line_circularity.csv")
aspect_ratio_df = pd.read_csv("./cell_line_aspect_ratio.csv")


# store tables in synapse
store_table(atomic_force_df, "Atomic force - calculated Young modulus and related spring constant", proj)
store_table(atomic_force_raw_df, "Atomic force - measurements", proj)

store_table(motility_df, "Motility - calculated end-to-end distance, total distance, speed, ", proj)
store_table(motility_raw_df, "Motility - measurements", proj)

store_table(traction_force_df, "Traction force and related cell volume, nuclear volume, cell area", proj)

store_table(proliferation_df, "Proliferation - single and touching cell counts over time", proj)
store_table(proliferation_samples_timing_df, "Proliferation - count measurement times", proj)

store_table(area_df, "Morphology - cell area", proj)
store_table(circularity_df, "Morphology - circularity", proj)
store_table(aspect_ratio_df, "Morphology - aspect ratio", proj)

syn.onweb(proj)
