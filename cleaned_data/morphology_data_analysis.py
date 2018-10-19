import os
import pandas as pd
import seaborn as sns
import random
import numpy as np
import matplotlib.pyplot as plt
from pylab import cm

def plot_morphology_dist(df, x, y, scale = "linear", title = "Cell line", color = "b", ax = None):

    if not ax:
        ax = sns.boxenplot(x=x, y=y, color=color, scale=scale, data=df)
    else:
        ax = sns.boxenplot(x=x, y=y, color=color, scale=scale, data=df, ax = ax)

    ax.set_title(title)

    return ax

plot_dir = "./figs"

morphology_df = pd.read_csv("./cell_line_morphology.csv")
print("Read data")
morphology_by_cl = morphology_df.groupby("cl_id")
print("Grouped data")


color_palettes = list(cm.datad.keys()) 
markers=["o", "s", "D", "x", "<", ">", "1"]

print(color_palettes)

for cl_id, morphology in morphology_by_cl:
    #filepath = os.path.join(plot_dir, condition_id + "_.pdf")
    #print("Working on " + condition_id)
    #plot_kde_facets(morphology, filepath)
 
    fig, axs = plt.subplots(nrows=3, figsize = (6, 10)) 

    area_ax = plot_morphology_dist(morphology, "condition_id", "area", title = "Area - cell line id: " + cl_id, color = "b", ax = axs[0])
    aspect_ratio_ax = plot_morphology_dist(morphology, "condition_id", "aspect_ratio", title = "Aspect ratio - cell line id: " + cl_id, color = "r", ax = axs[1])
    circularity_ax = plot_morphology_dist(morphology, "condition_id", "circularity", title = "Circularity - cell line id: " + cl_id, color = "g", ax = axs[2])
   
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "dist_by_condition_" + cl_id + ".png"), dpi = 300)


    g = sns.pairplot(morphology[["area", "circularity", "aspect_ratio", "condition_id"]], hue="condition_id", diag_kind="kde", palette = "tab20", markers = markers)
 
    for ax in g.axes.flat: 
        plt.setp(ax.get_xticklabels(), rotation=45)

    plt.tight_layout()
    g.add_legend(fontsize=14, bbox_to_anchor=(1.5,1))
    plt.savefig(os.path.join(plot_dir, "corr_plot_" + cl_id + ".png"), dpi = 300)
    
    
    g = sns.PairGrid(morphology[["area", "circularity", "aspect_ratio", "condition_id"]], hue="condition_id", palette = "tab20")
    g.map_upper(sns.regplot, truncate = True) 
    g.map_lower(sns.residplot) 
    #g.map_lower(sns.kdeplot)
    g.map_diag(sns.distplot, kde = False) 
 
    for ax in g.axes.flat: 
        plt.setp(ax.get_xticklabels(), rotation=45)
    
    g.add_legend() 
    g.set(alpha=0.5)

    plt.tight_layout()
    g.add_legend(fontsize=14, bbox_to_anchor=(1.5,1))
    plt.savefig(os.path.join(plot_dir, "fit_res_plot_" + cl_id + ".png"), dpi = 300)


    '''
    # plots 2D KDEs for morphology variables
    morphologies_by_condition = morphology.groupby(["condition_id"])

    f, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    for condition_id, morphology_by_condition in morphologies_by_condition:

        palette = color_palettes[random.randint(0, len(color_palettes))]
        print(palette)
        print(morphology_by_condition.head(10))
        ax = sns.kdeplot(morphology_by_condition.aspect_ratio, morphology_by_condition.circularity, cmap=palette, shade=True, shade_lowest=False)

        # Add labels to the plot
        condition_c = sns.color_palette(palette)[-2]
        ax.text(2.5, 8.2, condition_id, size=16, color=condition_c)

    plt.show()
    '''

    '''
    # plot regressions across variables
    g = sns.FacetGrid(morphology, col="condition_id", col_wrap=7, height=2, ylim=(0, 10))
    g.map(sns.regplot, "aspect_ratio", "circularity", color="c", ci=None, truncate = True);
    plt.show()
    '''
