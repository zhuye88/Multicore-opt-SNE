import numpy as np
import os
from MulticoreTSNE import MulticoreTSNE as TSNE
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import multiprocessing

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--n_threads", help='Number of threads', default=1, type=int)
parser.add_argument("--n_obs", help='How many observations (datapoints) to use', default=-1, type=int)
args = parser.parse_args()

def parse_csv(filepath):
    if not os.path.exists(filepath):
        raise RuntimeError("Cannot find file at " + filepath)
    mat = np.loadtxt(filepath, delimiter=',', skiprows=1)
    return mat

def plot(mat, colors):
    # labels = set(colors)
    colorsmat = colors.reshape((len(colors), -1)) # turns array into column
    matwithcolors = np.hstack((mat, colorsmat)) # append columnf
    returns = []
    cmap = cm.get_cmap('gist_ncar')
    uniques = np.unique(colors)
    index = 0
    for n in uniques:
        subset = matwithcolors[matwithcolors[:,2] == n] # rows where file index equals N
        cindex = float(index)/float(len(uniques))
        color = cmap( cindex )
        returns.append(plt.scatter(subset[:,0], subset[:,1], c=color, s=1))
        index+=1

    filename = "tsne_test.png"

    lgnd = plt.legend(returns,
           np.unique(colors),
           scatterpoints=1,
           bbox_to_anchor=(1,1),
           ncol=1,
           fontsize=8)
    for x in lgnd.legendHandles:
        x._sizes = [30]


    plt.savefig(filename)
    print("Example plot saved as tsne_test.png")


################################################################

data = parse_csv("bendall20k-data.csv")
classes = parse_csv("bendall20k-classes.csv")

if args.n_obs != -1 and args.n_obs <= len(data):
    data = data[:args.n_obs]
    classes = classes[:args.n_obs]

print("Available CPU cores detected: " + str(multiprocessing.cpu_count()))

tsne = TSNE(n_jobs=int(args.n_threads), verbose=3, random_state=2, auto_iter=True, learning_rate=len(data)/12, auto_iter_end=1000)
tsne_result = tsne.fit_transform(data)

plot(tsne_result, classes)
