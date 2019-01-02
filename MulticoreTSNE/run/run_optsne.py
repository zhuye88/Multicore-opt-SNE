from __future__ import print_function
import numpy as np
import os
from MulticoreTSNE import MulticoreTSNE as TSNE
import matplotlib.pyplot as plt
import multiprocessing

import argparse

default_result_path = "tsne_results.csv"

parser = argparse.ArgumentParser()
parser.add_argument("--data", help='Path to data file')
parser.add_argument("--n_threads", help='Number of threads', default=1, type=int)
parser.add_argument("--learning_rate", help='Learning rate', default=-1, type=float)
parser.add_argument("--n_iter_early_exag", help='Number of iterations out of total to spend in early exaggeration', default=250, type=int)
parser.add_argument("--n_iter", help='Total number of iterations', default=1000, type=int)
parser.add_argument("--perp", help='Perplexity', default=30.0, type=float)
parser.add_argument("--theta", help='Theta', default=0.5, type=float)
parser.add_argument("--optsne", help='Whether or not to use opt-SNE mode (no argument, just flag)', default=False, action='store_true')
parser.add_argument("--optsne_end", help='Constant used to stop run when (KLDn-1 - KLDn) < KLDn/X where X is this arg', default=5000, type=float)
parser.add_argument("--early_exaggeration", help='Early exaggeration factor', default=12, type=float)
parser.add_argument("--n_obs", help='How many observations (datapoints) to use', default=-1, type=int)
parser.add_argument("--seed", help='Random seed for t-SNE', default=42, type=int)
parser.add_argument("--verbose", help='Print progress every N iterations', default=25, type=int)
parser.add_argument("--outfile", help='Relative or absolute filepath at which to save results CSV', default=default_result_path)
args = parser.parse_args()

def parse_csv(filepath):
    if not os.path.exists(filepath):
        raise RuntimeError("Cannot find file at {}".format(filepath))
    mat = np.loadtxt(filepath, delimiter=',', skiprows=1)
    return mat

################################################################

data = parse_csv(args.data)

if args.n_obs != -1 and args.n_obs <= len(data):
    data = data[:args.n_obs]

if args.learning_rate == -1:
    if not args.optsne:
        args.learning_rate = 200
    else:
        args.learning_rate = len(data)/args.early_exaggeration

tsne = TSNE(n_jobs=int(args.n_threads),
            learning_rate=args.learning_rate,
            n_iter=args.n_iter,
            n_iter_early_exag=args.n_iter_early_exag,
            perplexity=args.perp,
            angle=args.theta,
            auto_iter=args.optsne,
            auto_iter_end=args.optsne_end,
            early_exaggeration=args.early_exaggeration,
            random_state=args.seed,
            verbose=args.verbose,
            )

if args.verbose:
    print("Available CPU cores detected: {}".format(str(multiprocessing.cpu_count())))
tsne_result = tsne.fit_transform(data)
try:
    np.savetxt(args.outfile, tsne_result, delimiter=",")
    if args.verbose:
        print("Results saved as {}".format(args.outfile))
except:
    print("can't write to {}. Is path valid?".format(args.outfile))
    np.savetxt(default_result_path, tsne_result, delimiter=",")
    if args.verbose:
        print("Results saved as {}".format(default_result_path))
