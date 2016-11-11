#!/usr/bin/python
# -*- coding: utf-8 -*-

import os


stem_dic = {"full": "test", "test": "full"}

prog_files = os.path.dirname(os.path.realpath(__file__))

files = os.listdir(prog_files)

stimuli_files = [f for f in files if "stimuli" in f]

stimuli_stems =  [f[-8:-4] for f in stimuli_files]

stimuli_new_stems = [stem_dic[s.lower()] for s in stimuli_stems]

def rename(n, stem_new):
    n_new = n[0:-8] + stem_new + ".csv"
    return n_new

stimuli_new_names = [rename(f, s) 
                     for f, s in zip(stimuli_files, stimuli_new_stems)]


old_fnames = [os.path.join(prog_files, s) for s in stimuli_files]
new_fnames = [os.path.join(prog_files, s) for s in stimuli_new_names]

[os.rename(old, new) for old, new in zip(old_fnames, new_fnames)]

print stimuli_stems
print stimuli_new_stems
print stimuli_new_names
