#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A logical agent navigating the roboto delivery world."""

from __future__ import print_function
import pycosat
import sys
import pdb

#################################################################
#
# Functions for interfacing PicoSAT
#
#################################################################

atoms_list = []


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
    return ((n + 1) * inv)


def n2s(n):
    """Convert numeric representation of atom to string."""
    r = atoms_list[abs(n) - 1]
    if (n) < 0:
        r = '~' + r
    return (r)


def solve(axioms):
    picosatInput = map(lambda c: map(lambda s: s2n(s), c), axioms)
    picosatSolution = pycosat.solve(picosatInput)
    if (picosatSolution == 'UNSAT'):
        return (picosatSolution)
    else:
        return (map(lambda atom: n2s(atom), picosatSolution))


def get_name(index):
    if index == 0:
        return "Wolf "
    elif index == 1:
        return "Goat "
    elif index == 2:
        return "Cabbage "
    else:
        return "Ferry"


def change_state(state, a):
    if a == "wolf_ab":
        return "b" + state[1:3] + "b"
    elif a == "goat_ab":
        return state[:1] + "b" + state[2:3] + "b"
    elif a == "cabbage_ab":
        return state[:2] +"bb"
    elif a == "ferry_ab":
        return state[:3] + "b"
    elif a == "wolf_ba":
        return state[:0] + "a" + state[1:2] + "a"
    elif a == "goat_ba":
        return state[:1] + "a" + state[2:3]+"a"
    elif a == "cabbage_ba":
        return state[:2] +"aa"
    elif a == "ferry_ba":
        return state[:3] + "a"


def pretty_print(action_trace, action_list):
    state = "aaaa"
    print_state(state)
    for a in action_trace:
        state = change_state(state, action_list[action_trace.index(a)])
        print_state(state)


def print_state(state):
    a_list = ""
    b_list = ""
    for index, l in enumerate(state):
        if l == "a":
            a_list += get_name(index)
        else:
            b_list += get_name(index)
    print(a_list + "~~~~~~~~~~~~~~~~~" + b_list)

def print_actions_in(clause):
    # Print all positive actions in clause.
    action_trace = []
    action_list = []
    for c in clause:
        for a in actions:
            if (c.find(a) == 0):
                action_trace += [c]
                action_list += [a]
    for a in action_trace[:-1]:
        print(a)
    pretty_print(action_trace[:-1],action_list[:-1])


#################################################################
#
# Axioms about the world
#
#################################################################

actions = ['wolf_ab', 'goat_ab', 'cabbage_ab', 'ferry_ab', 'wolf_ba', 'goat_ba', 'cabbage_ba', 'ferry_ba']


# Movement axioms

def movement_axioms(t):
    """All movmement axioms for time t."""
    # Movement plan
    # Format: State,
    #         'wolf_ab', 'goat_ab', 'cabbage_ab', 'ferry_ab', 'wolf_ba', 'goat_ba', 'cabbage_ba', 'ferry_ba'
    # Movement axioms
    states = [
        ['wgc_abaa',
         'wgc_bbab', 'wgc_abaa', 'wgc_abbb', 'wgc_abab', 'wgc_abaa', 'wgc_abaa', 'wgc_abaa', 'wgc_abaa']
        #             keine Ziege a                       -> falsche Richtung
        , ['wgc_abab',
           'wgc_abab', 'wgc_abab', 'wgc_abab', 'wgc_abab', 'wgc_abab', 'wgc_aaaa', 'wgc_abab', 'wgc_abaa']
        #                               <-  falsche Richtung, kein wolf b             kein kohl b
        , ['wgc_bbab',
           'wgc_bbab', 'wgc_bbab', 'wgc_bbab', 'wgc_bbab', 'wgc_abaa', 'wgc_baaa', 'wgc_bbab', 'wgc_bbab']
        #                               <-falsche Richtung                         kein kohl b  Ziege weg
        , ['wgc_abbb',
           'wgc_abbb', 'wgc_abbb', 'wgc_abbb', 'wgc_abbb', 'wgc_abbb', 'wgc_aaba', 'wgc_abaa', 'wgc_abbb']
        #                               <-falsche Richtung  kein wolf b                        Kohl weg
        , ['wgc_aaba',
           'wgc_babb', 'wgc_abbb', 'wgc_aaba', 'wgc_aaba', 'wgc_aaba', 'wgc_aaba', 'wgc_aaba', 'wgc_aaba']
        #                           kein Kohl a  Ziege weg  ->falsche Richtung
        , ['wgc_babb',
           'wgc_babb', 'wgc_babb', 'wgc_babb', 'wgc_babb', 'wgc_aaba', 'wgc_babb', 'wgc_baaa', 'wgc_baba']
        #                              <-falsche Richtung             keine ziege b
        , ['wgc_baaa',
           'wgc_baaa', 'wgc_bbab', 'wgc_babb', 'wgc_baaa', 'wgc_baaa', 'wgc_baaa', 'wgc_baaa', 'wgc_baaa']
        # kein wolf a                          kohl weg   ->falsche Richtung
        , ['wgc_baba',
           'wgc_baba', 'wgc_bbbb', 'wgc_baba', 'wgc_babb', 'wgc_baba', 'wgc_baba', 'wgc_baba', 'wgc_baba']
        #  kein wolf a             kein kohl a            ->falsche Richtung
        , ['wgc_bbbb',
           'wgc_bbbb', 'wgc_bbbb', 'wgc_bbbb', 'wgc_bbbb', 'wgc_bbbb', 'wgc_baba', 'wgc_bbbb', 'wgc_bbbb']
        #                              <-falsche Richtung   kohl weg               ziege weg    ziege,kohl weg
        , ['wgc_aaaa',
           'wgc_aaaa', 'wgc_abab', 'wgc_aaaa', 'wgc_aaaa', 'wgc_aaaa', 'wgc_aaaa', 'wgc_aaaa', 'wgc_aaaa']
        # kohl weg,              ziege weg    ziege,kohl weg  -> falsche Richtung
    ]

    locations = [l[0] for l in states]
    room_links = []
    # Movement axioms
    for l in states:
        room = l[0]
        for (direction, connection) in zip(actions,
                                           l[1:]):
            # room_t ∧ direction_t → connection_t+1
            room_links += [['~%s_%d' % (room, t),
                            '~%s_%d' % (direction, t),
                            '%s_%d' % (connection, t + 1)]]
    # Location does not change  if we do not move
    # robot_at_x ∧ ~north ∧ ~south ∧ ~west ∧ ~east → robot_at_x_t+1
    # = ¬robot_at_x ∨ north ∨ south ∨ west  ∨east ∨ robot_at_x_t+1
    no_move_no_location_change = []
    for l in locations:
        no_move_no_location_change += [['~%s_%d' % (l, t),
                                        'wolf_ab_%d' % t,
                                        'goat_ab_%d' % t,
                                        'cabbage_ab_%d' % t,
                                        'ferry_ab_%d' % t,
                                        'wolf_ba_%d' % t,
                                        'goat_ba_%d' % t,
                                        'cabbage_ba_%d' % t,
                                        'ferry_ba_%d' % t,
                                        '%s_%d' % (l, t + 1)]]

    # There is only one robot
    # (¬ robot_at_main_office_t ∨ ¬ robot_at_mail_drop_t) ∧
    # (¬ robot_at_main_office_t ∨ ¬ robot_at_o101_t) ∧
    # (¬ robot_at_mail_drop_t ∨ ¬ robot_at_o101_t) ∧
    # ...
    only_one_robot = []
    for l0 in range(len(locations)):
        for l1 in range(l0 + 1, len(locations)):
            only_one_robot += [['~%s_%d' % (locations[l0], t),
                                '~%s_%d' % (locations[l1], t), ]]

    # Exactly one action at a time:
    one_action_a_time = []
    # At least one action at a time
    # north_t ∨ south_t ∨ west_t ∨ east_t ∨ pick_up_t ∨ drop_t
    one_action_a_time += [['%s_%d' % (l, t) for l in actions]]
    # At most one action at a time
    for a0 in range(len(actions)):
        for a1 in range(a0 + 1, len(actions)):
            if (a0 != a1):
                one_action_a_time += [['~%s_%d' % (actions[a0], t),
                                       '~%s_%d' % (actions[a1], t)]]
    return (room_links
            + no_move_no_location_change
            + only_one_robot
            + one_action_a_time
            )


#################################################################
#
# Reasoning about the world
#
#################################################################

t_max = 20
axioms_up_to_time_t = []
for t in range(0, t_max + 1):
    axioms_up_to_time_t += movement_axioms(t)
    axioms = (axioms_up_to_time_t +
              [  # Start position of agent
                  ['wgc_aaaa_0']
                  # Target position for mail
                  , ['wgc_bbbb_%d' % t]
              ])
    solution = solve(axioms)
    if (solution != 'UNSAT'):
        print("Found a solution:")
        print_actions_in(solution)
        sys.exit(0)
print("Not possible in up to %d steps. :-(" % t_max)
