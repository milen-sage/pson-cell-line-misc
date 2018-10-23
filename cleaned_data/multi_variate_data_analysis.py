import os
import pandas as pd
import seaborn as sns
import random
import numpy as np
import matplotlib.pyplot as plt
from pylab import cm

def label_cancer(row):
    if row["disease"] == "NORMAL":
        return "NORMAL"
    else:
        return "CANCER"

def plot_single_var_dist(df, x, y, scale = "linear", title = "Cell line", color = "b", ax = None):

    if not ax:
        ax = sns.boxenplot(x=x, y=y, color=color, scale=scale, data=df)
    else:
        ax = sns.boxenplot(x=x, y=y, color=color, scale=scale, data=df, ax = ax)

    ax.set_title(title)

    return ax

def plot_anova_cat(data, x, y, hue, col, palette = "YlGnBu_d", kind = "bar", basename = "", ci = float):

    g = sns.catplot(x=x, y=y, hue=hue, col=col,
                    capsize=.2, palette=palette, height=6, aspect=.75,
                    kind=kind, data=data, ci = ci)

    g.despine(left=True)

    plt.tight_layout()
    g.add_legend(fontsize=14, bbox_to_anchor=(1.5,1))
    plt.savefig(os.path.join(plot_dir, basename + suffix + ".png"), dpi = 300)


if __name__ == "__main__":


    plot_dir = "./figs"
    suffix = "_by_tissue"

    morphology_df = pd.read_csv("./cell_line_morphology.csv")
    motility_df = pd.read_csv("./summary_motility_data.csv")
    cell_line_df = pd.read_csv("./cell_lines.csv")
    condition_df = pd.read_csv("./conditions.csv")

    motility_cl_df = motility_df.merge(cell_line_df, how = "left", on = "cl_id")
    motility_cl_df = motility_cl_df.merge(condition_df, how = "left", on = "condition_id")
    motility_cl_df["diagnosis"] = motility_cl_df.apply(label_cancer, axis = 1)
    motility_cl_df.sort_values("stiffness", inplace = True)

    aspect_ratio_df = morphology_df.groupby(["cl_id", "condition_id"])["aspect_ratio"].agg({"avg_aspect_ratio":np.mean}).reset_index()
    print(aspect_ratio_df)
    circularity_df= morphology_df.groupby(["cl_id", "condition_id"])["circularity"].agg({"avg_circularity":np.mean}).reset_index()
    print(circularity_df)
    area_df = morphology_df.groupby(["cl_id", "condition_id"])["area"].agg({"avg_area":np.mean}).reset_index()
    print(area_df) 


    morphology_cl_df = aspect_ratio_df
    morphology_cl_df["avg_circularity"] = circularity_df["avg_circularity"].values
    morphology_cl_df["avg_area"] = area_df["avg_area"].values

    print(morphology_cl_df)

    '''
    sns.set(style="whitegrid")

    x = "diagnosis"
    hue = "tissue"
    col = "condition"
    palette = "tab20"
    kind = "point"
    ci = None

    plot_anova_cat(motility_cl_df, x, "avg_end_to_end_dist", hue, col, palette = palette, kind = kind, basename = "end_to_end_dist", ci = None)
    plot_anova_cat(motility_cl_df, x, "avg_speed", hue, col, palette = palette, kind = kind, basename = "speed", ci = None)
    plot_anova_cat(motility_cl_df, x, "avg_total_dist", hue, col, palette = palette, kind = kind, basename = "total_dist", ci = None)
    '''


