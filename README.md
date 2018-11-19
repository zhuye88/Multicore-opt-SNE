# opt-SNE
opt-SNE is a modified version of t-SNE that enables high-quality embeddings in the optimal amount of compute time without having to empirically tune algorithm parameters. For thorough background and discussion on this work, please read [the paper](https://doi.org/10.1101/451690).

This repository contains a C++ implementation with a Python wrapper.

Need help getting this code running? [Contact Omiq](https://omiq.ai/#contact).

# What is the Benefit?
We generally observe these benefits using the opt-SNE methodology compared to previously conventional strategies for running t-SNE:
- High-quality embeddings ~2-5x faster
- Reliable embedding of datasets with numbers of observations that were previously prohibitively large (see the paper for examples of embedding with 5.2 * 10^6 and 2 * 10^7 datapoints)
- Improved local structure resolution
- Avoiding the expensive scenario of having to do multiple runs to optimize settings if the initial run failed to produce a good embedding

<p align="center">
  <img src="tsnevsoptsne.png"><br>
  <em>20 million datapoint embedding. Left: conventional t-SNE approach. Right: opt-SNE.</em>
</p>

# How Does opt-SNE Work?
opt-SNE automates the selection of three important parameters for the t-SNE run:
1) initial learning rate
2) number of iterations spent in early exaggeration
3) number of total iterations.

Learning rate is calculated before the run begins using a formula. The number of iterations for early exaggeration and the run itself are determined in real time as the run progresses by monitoring the Kullback-Leibler divergence (KLD). More details are given directly below.

The algorithm works in this fashion:
- First calculate the optimal initial learning rate (aka "eta") based on the number of observations (aka "cells", "samples", "rows") in the dataset. The value is given by the number of observations divided by the early exaggeration factor, which in most implementations is 12 by default. It may be exposed as an argument, such as in this package with the `early_exaggeration` argument.
- As the run progresses the Kullback-Leibler divergence (KLD) is monitored. The difference and rate of change are calculated for readings between iterations.
- By monitoring KLD rate of change (KLDRC), a local maximum can be detected. When this maximum is reached, the run switches out of early exaggeration.
- After early exaggeration the KLD difference is used to stop the run. This happens when the difference from one iteration to the next is less than the current KLD divided by a constant which can be overridden by the user. The larger this constant is, the longer the run will go before stopping.

In our experience, tweaking the other arguments to t-SNE (at least in context of single-cell data), doesn't meaningfully change results and is more a matter of taste for impacting how certain characteristics of the final embedding appear. We have seen that reasonable modifications to other parameters such as `perplexity` and `early_exaggeration` factor don't impact the opt-SNE methodology. We haven't tested `theta`, but we generally advise not modifying this parameter (at least for single-cell data).

# Installation
## Mac OSX
These directions assume little to no experience with programming or environment/dependency management.
- Download this repo to a local folder.
- Open the Terminal app.
- Install [Homebrew](https://brew.sh/) using the directions on their website.
- Use Homebrew to install cmake. The command to enter in Terminal is `brew install cmake`.
- Use Homebrew to install python 2.x. The command is `brew install python@2`.
- Use Homebrew to install GCC version 8. The command is `brew install gcc@8`.
- Set the working directory in Terminal to the folder you downloaded locally in the first step. Don't know how to do that? type the letters `cd ` (with a space afterwards) and then drag the folder into the terminal. Its path should appear. Submit the command and then the current directory of Terminal should be set to the correct folder. Typing `pwd` should indicate being inside the directory and `ls` should show the files present inside it.
- Enter the command `pip2 install matplotlib` to install this dependency that is only necessary for running `test.py` below.
- Enter the command `pip2 install .` to install this package.
- Enter the command `python2 MulticoreTSNE/examples/test.py --n_threads 2`
  - After submitting this command, a statement should be printed that indicates how many cores are available on your machine and how many are being used by the algorithm. If the number is not 2, then the installation is not correctly configured for parallel processing. This won't affect results but will affect speed, assuming your computer has more than one CPU core.

# Usage
A script `run_optsne.py` is included that allows this package to be run from the command line on any CSV file. Alternatively, it can be imported as a Python module to run on any matrix data as desired.

## Mac OSX Terminal
- Follow the directions above to install the package.
- If not already done per above, open the Terminal app and set the working directory to this repo.
- Run with the command `python2 MulticoreTSNE/run/run_optsne.py --optsne --data <path_to_data>`. This is the minimal command necessary to run opt-SNE with all default parameters. Replace `<path_to_data>` with the filepath to a CSV file. Additional parameters can be specified to override defaults (see Arguments section below).

## CSV Formatting Requirements
- The file must have one line of buffer (usually used for column names, but it doesn't matter what is in this line of the file).
- Only the columns desired for analysis should be present in the file. There is no filtering mechanism for columns.
- For an example, see **bendall20k-data.csv** in this repo.
- Note to single-cell data users: make sure the data are properly scaled/compensated/normalized/etc as relevant before use.

## Arguments
### Public Arguments
Add these flags followed directly by values to run_optsne.py to modify algorithm behavior. E.g., `python2 MulticoreTSNE/run/run_optsne.py --optsne --data bendall20k-data.csv --n_threads 4 --perp 50 --n_obs 5000 --verbose 20`. These flags describe arguments to the command line script only. They generally map to the python package itself but some have slightly different names.
- `--data` is the filepath to the data CSV file to be run through the algorithm.
- `--n_threads` is the number of CPU threads to use.
- `--learning_rate` is the learning rate (aka "eta"). This is set automatically of running in opt-SNE mode but can be overridden if given as an argument.
- `--n_iter_early_exag` is the number of iterations out of total to spend in early exaggeration. If running in opt-SNE mode this argument is ignored.
- `--n_iter` is the total number of iterations. If running in opt-SNE mode this argument is used to stop the run if opt-SNE has not already done so by this point.
- `--perp` is perplexity.
- `--theta` is theta (aka "angle").
- `--optsne` is a flag with no accompanying value. If this flag if present, t-SNE will run in opt-SNE mode. If not present, it runs in normal t-SNE mode.
- `--optsne_end` is the constant used to stop the run. See discussion above about how opt-SNE functions for more discussion.
- `--early_exaggeration` is the early exaggeration factor.
- `--n_obs` is the number of observations (datapoints) to use from the data file if not the whole set.
- `--seed` is the pseudorandom seed value in order to control consistency of results between runs as desired.
- `--verbose` is the frequency in iterations to print algorithm progress. Pass 0 to have no printed output, 1 for every iteration, 25 for every 25 iterations, etc.

### Private Arguments
There are also a number of tuneable parameters that are currently hard-coded. Their values can be edited with the **tsne.cpp** file. They will take effect after reinstalling the package following the edits.
- `auto_iter_buffer_ee` is the number of iterations to wait before starting to monitor KLDRC for stopping early exaggeration.
- `auto_iter_buffer_run` is the number of iterations to wait before starting to monitor KLD for stopping the run after early exaggeration.
- `auto_iter_pollrate_ee` is how frequently in iterations the KLD should be calculated for purposes of switching out of early exaggeration.
- `auto_iter_pollrate_run` is how frequently in iterations the KLD should be calculated for purposes of ending the run.
- `auto_iter_ee_switch_buffer` is the number of iterations times the `auto_iter_pollrate_ee` to wait after detecting KLDRC switchpoint to actually make the switch out of EE.

# Does opt-SNE Work for My Data?
This methodology is general and should work broadly, however, it has been most closely characterized with single-cell data types such as flow cytometry, mass cytometry, and scRNA-seq. It has also been tested on MNIST 70000x784.

# Code Origination and Discussion
This package is forked from Dmitry Ulyanov's [Multicore t-SNE](https://github.com/DmitryUlyanov/Multicore-TSNE) which itself is a multicore modification of [Barnes-Hut t-SNE](https://github.com/lvdmaaten/bhtsne) by L. Van der Maaten.

Multicore t-SNE was chosen as the base for this package due to its speed. See the original repository for information on benchmarks.

Note that there is an edit to the CMakeLists.txt file that was made for compatibility with Mac OSX. Other environments may require backing this edit out or otherwise augmenting this file.

It should be noted that the behavior of KLDRC is markedly different between Barnes-Hut t-SNE and Multicore t-SNE. Specifically, early oscillations in KLDRC are much more dramatic in Multicore t-SNE, whereas they are barely detectible in Barnes-Hut t-SNE. What code difference between the packages specifically accounts for this difference is currently unclear, but it doesn't seem to materially impact results nor the applicability of the opt-SNE methodology. It's referenced here simply as a note to the astute reader who notices that KLDRC graphs produced from this package do not match those reported in the paper, since the paper was written using the Barnes-Hut implementation.

At such a time that this methodology gains acceptance more generally it can be integrated into the canonical t-SNE implementations and this fork can be deprecated.

# License
Inherited from [original repo's license](https://github.com/lvdmaaten/bhtsne).

# Future Work
- It could make sense to take a more functional approach to the criteria for early exaggeration switch and stopping the run in case different logic is desired without having to fork new versions of this package.

# Citation
If you use the opt-SNE methodology, please cite the [preprint](https://doi.org/10.1101/451690):

Anna C. Belkina, Christopher O. Ciccolella, Rina Anno, Josef Spidlen, Richard Halpert, Jennifer Snyder-Cappione. **Automated optimal parameters for T-distributed stochastic neighbor embedding improve visualization and allow analysis of large datasets (2018)** bioRxiv 451690; 
**doi**: https://doi.org/10.1101/451690

For Multicore-TSNE:
```
@misc{Ulyanov2016,
  author = {Ulyanov, Dmitry},
  title = {Multicore-TSNE},
  year = {2016},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/DmitryUlyanov/Multicore-TSNE}},
}
```

Of course, do not forget to cite [L. Van der Maaten's paper](http://lvdmaaten.github.io/publications/papers/JMLR_2014.pdf)
