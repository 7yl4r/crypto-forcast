"""
t-distributed Stochastic Neighbor Embedding (t-SNE) visualization of classes
in hyperplane.

Based on: https://blog.applied.ai/visualising-high-dimensional-data/
"""
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import seaborn as sns
from sklearn.preprocessing import StandardScaler


print(__doc__)

def main(fname, var1, var2, var3):
    # master_dataframe_ is exported by class_subset_vs_all_dists
    df = pd.read_csv(fname)
    df = df.dropna()

    tsne = TSNE(
        n_components=2, random_state=0,
        perplexity=30  # should be ~ size of smallest expected cluster
    )

    assert len(df["score"]) > 0
    dfsvd = df - df["score"]  # TODO: fix syntax to cp df & rm score col
    print(dfsvd.shape)
    print("building tsne using :")
    print(dfsvd.head())

    # TODO: should we scale here or use raw values?
    X = StandardScaler().fit_transform(dfsvd.values)
    # X = dfsvd.values
    Z = tsne.fit_transform(X)
    dftsne = pd.DataFrame(Z, columns=['x', 'y'], index=dfsvd.index)
    # === calc 3 color components from selected variables in df
    MAX_COLOR = 255
    dftsne['r'] = MAX_COLOR * (df[var1] - min(df[var1]))/max(df[var1])
    dftsne['g'] = MAX_COLOR * (df[var2] - min(df[var2]))/max(df[var2])
    dftsne['b'] = MAX_COLOR * (df[var3] - min(df[var3]))/max(df[var3])
    # TODO: fix base16 conversion here
    dftsne['color'] = (  # hexidecimal color code
        '#' + base16(dtfsne['r']) +
        '#' + base16(dtfsne['g']) +
        '#' + base16(dtfsne['b'])
    )
    MIN_SIZE = 1
    MAX_SIZE = 10
    dftsne['size'] = (
        MAX_SIZE * (df['score'] - min(df['score']))/max(df['score']) + MIN_SIZE
    )
    g = sns.lmplot(
        'x', 'y', dftsne, hue='color', fit_reg=False, size=8,
        scatter_kws={'alpha': 0.7, 's': 60},
        size='size'  # TODO: is this supported?
    )
    g.axes.flat[0].set_title(
        'Scatterplot of data reduced to 2D using t-SNE ' +
        'Colorized R={} G={} B={}. '.format(var1, var2, var3) +
        'Point size is score.'
    )

    plt.show()

if __name__ == "__main__":
    main('sample_data.csv', 'var1', 'var2', 'var3')
