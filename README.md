# GIS1 Contouring Scripts
This project is a collection of scripts to automate the process of producing contour lines for the USA Contours 
clearinghouse website.

## Background
Previously, the `Z:\Scripts` folder was a simple bucket for any and all scripts related to producing contour lines, 
and included several different iterations of the contouring model script and other supporting scripts over time. 
However, as updates to these files have been made over time, many files in this directory have become outdated and are
no longer used, and only add confusion as to which script is the "current" version or the "correct" one to use for a 
given scenario.

Furthermore, the separation of the `Z:\Clearinghouse_Support` and `Z:\Scripts` folders was unnecessary and made it
more difficult to work on both sets of scripts at the same time. Ths, the former `Z:\Scripts` folder has been merged
into the `Z:\Clearinghouse_Support` folder.
- `data` - Source data files for the entire country, including but not limited to state, county, and USGS project
boundaries, UTM and SP tile grids, and USGS project allocations for each state/county
    - Note, this folder is NOT tracked with Git (see details below), and thus cannot be recovered if changed or deleted
- `docs` [Formerly in `Z:\Scripts`] - Notes and other documentation files
- `js` - JavaScript processing scripts (primarily used for the production of source data in the `data` folder)
- `python` [Formerly in `Z:\Scripts`] - Contains all of the up-to-date and actively used python scripts related to 
producing and transfering contour line files
- `review_and_possibly_delete` [Formerly in `Z:\Scripts`] - Previously written scripts, logs, and documentation files
which are likely no longer relevant given recent updates, and should be considered for deletion

## Current Organization
All of the latest versions of the contouring and other supporting scripts are included directly in the root of this
folder. Where necessary, scripts and other files were renamed to favor simple naming conventions that are easy to
reference. Each script file should contain a more verbose description of its purpose and function as comments at the
top of the file.

All of the seemingly "old" and "unused" scripts and files have been moved to the `review_and_possibly_delete` folder.
As the name suggests, at a later date, we should review each of these files and delete them if necessary. to reduce
clutter and potential confusion.

### Git Version Management
This folder (ie "repository") is now tracked using the code version managemnt tool known as Git. Git is used in code 
projects all over the world to help developers track changes in their code over time (ie "commits"), to roll back to 
previous versions if something went wrong (ie "revert"), to create different versions of their code with different 
sets of features (ie different "branches"), to combine different branches together (ie "merge"), and much more. It also 
allows developers to add a comment (ie "commit message") on each change they make, and to label (ie "tag") specific 
versions (ie "commits") with a version number or other convenient name to easily identify and find previous versions in 
the history (ie "commit tree").

Thus, any scripts or files that have been deleted from this folder or otherwise changed in an undesirable way can
ALWAYS be recovered by simply rolling back to a previous commit in the tree.

#### Aside: How Git Works
If you're not familiar with Git, the way that it works is that it tracks all of the changes in your files as "deltas" 
which are stored in a database in the hidden `.git` subfolder in the project's root folder. When switching between 
different versions of files, the actual files from the project  folder on the hard drive of this computer are 
effectively deleted, and an old version of the files are inserted in their place. That is, the actual files and their
contents on the hard drive actually change. Again, all of the different versions are stored as deltas in a database (in 
other words, instructions on what files and content should be added and deleted for a given version), and not as 
separate "copies" of the same file. Not only is this more efficient from a storage standpoint, but it also keeps your
file system clean and easy to navigate. Rather than navigating to a separate folder or opening a file with a different
name as a way of differentiating between different versions of a file, only one version of that file exists at a time,
and you can use Git to quickly change which version is currently present.
