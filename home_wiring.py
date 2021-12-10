#! /usr/bin/env python3
## BEGIN CODE SNIPPET: "home_wiring.py"
"""A little diagnostics example."""

# We use PicoSAT to handle propositional logic.
# The Python binding for PicoSAT is available at
# <https://github.com/ContinuumIO/pycosat>.
#
# PicoSat expects input in DIMACS CNF format; see for example
# <http://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html>. Most of the
# Python code deals with converting a more human readable format to
# DIMACS CNF.

import pycosat
import pdb

#################################################################
#
# Functions for interfacing PicoSAT
#
#################################################################

def s2n(s):
    """Convert string representation of atom to number."""
    if (s[0] == '~'):
        inv = -1
        t = s[1:]
    else:
        inv = 1
        t = s
    try:
        n = atoms_list.index(t)
    except:
        # Atom not in list. Add it.
        atoms_list.append(t)
        n = len(atoms_list) - 1
    return((n+1) * inv)

def n2s(n):
    """Convert numeric representation of atom to string."""
    r = atoms_list[abs(n)-1]
    if (n) < 0:
        r = '~' + r
    return(r)

def solve(axioms):
    picosatInput = map(lambda c: map(lambda s: s2n(s), c), axioms)
    picosatSolution = pycosat.solve(picosatInput)
    if (picosatSolution == 'UNSAT'):
        return(picosatSolution)
    else:
        return(map(lambda atom: n2s(atom), picosatSolution))

#################################################################
#
# Axiomatization of the problem
#
#################################################################

# In our diagnostics example, we use the following symbolic names for
# atoms.
atoms_list = [ 'live_l_1' , 'live_w_0' , 'live_w_0' , 'live_w_1' , 'up_s_2'
             , 'live_w_0' , 'live_w_2' , 'down_s_2' , 'live_w_1' , 'live_w_3'
             , 'up_s_1' , 'live_w_2' , 'live_w_3' , 'down_s_1' , 'live_l_2'
             , 'live_w_4' , 'live_w_4' , 'live_w_3' , 'up_s_3' , 'down_s_3'
             , 'live_p_1' , 'live_w_3' , 'live_w_3' , 'live_w_5' , 'ok_cb_1'
             , 'live_p_2' , 'live_w_6' , 'live_w_6' , 'live_w_5' , 'ok_cb_2'
             , 'live_w_5' , 'live_outside' , 'lit_l_1' , 'live_l_1' , 'ok_l_1'
             , 'lit_l_2' , 'live_l_2' , 'ok_l_2' , 'live_p_1' , 'live_p_2'
             ]

# Here come the axioms about the world of the diagnostics problem.
# This is a formula in CNF, where negated atoms are indicated by the
# prefix '~'.
axioms = [ ['live_l_1', '~live_w_0']
         , ['live_w_0', '~live_w_1', '~up_s_2']
         , ['live_w_0', '~live_w_2', '~down_s_2']
         , ['live_w_1', '~live_w_3', '~up_s_1']
         , ['live_w_2', '~live_w_3', '~down_s_1']
         , ['live_l_2', '~live_w_4']
         , ['live_w_4', '~live_w_3', '~up_s_3']
         , ['live_p_1', '~live_w_3']
         , ['live_w_3', '~live_w_5', '~ok_cb_1']
         , ['live_p_2', '~live_w_6']
         , ['live_w_6', '~live_w_5', '~ok_cb_2']
         , ['live_w_5', '~live_outside']
         , ['lit_l_1', '~live_l_1', '~ok_l_1']
         , ['lit_l_2', '~live_l_2', '~ok_l_2']
         , ['live_p_1', '~live_w_3']
         , ['live_p_2', '~live_w_6']
         ]

# Our diagnosis tools works as follows. We have three sets of
# formulas, split into axioms, everythingOK, and observations.
#
# The axioms describe the laws of our world, i.e. they
# will always hold.
#
# The observations are a list of atoms that we observe to be true.
#
# everythingOK contains a list of atoms that may or may not be
# true. These are the potential errors.

# When trying to identify the error(s), we negate elements of list
# everythingOK and check if the problem becomes satisfiable. If it
# becomes satisfiable, then we have identified a potential error.

# We provide two functions to generate these negations. Function
# allNegations generates all possible combinations of negated and
# non-negated elements of list everythingOK, i.e. it generates all
# possible combinations of error conditions. Function singleNegations
# negates only one element of list everythingOK, i.e. it generates all
# single error conditions.

# Try running the diagnosis both with allNegations and with
# singleNegations and compare the results.

def allNegations(c):
    if (len(c) == 0):
        return([[]])
    else:
        r = allNegations(c[1:])
        return([[c[0]] + x for x in r] +
               [['~' + c[0]] + x for x in r])
        

def singleNegations(c):
    r = []
    for i in range(len(c)):
        e = c[:]
        e[i] = '~' + e[i]
        r.append(e)
    return(r)

def diagnosis():
    everythingOK = [  'live_outside'
                    , 'ok_cb_1'
                    , 'ok_cb_2'
                    , 'ok_l_1'
                    , 'ok_l_2'
                   ]
    observations = [  'up_s_1'
                    , 'up_s_2' 
                    , '~lit_l_1'
                   ]
    clauses = (axioms +
               list(map(lambda x: [x], everythingOK)) +
               list(map(lambda x: [x], observations)))
    solution = solve(clauses)
    if (solution == 'UNSAT'):
        print('Something is wrong. I will try to identify \
possible sources of the defect ...')
#        possibleErrors = allNegations(everythingOK)
        possibleErrors = singleNegations(everythingOK)
        for e in possibleErrors:
            clauses = (axioms +
                       list(map(lambda x: [x], e)) +
                       list(map(lambda x: [x], observations)))
            if (solve(clauses) != 'UNSAT'):
                print("\nPossible cause of error:")
                for c in e:
                    print(c)

if __name__ == "__main__":
    diagnosis()

## END CODE SNIPPET
