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
    if(s[0] == '~'):
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
    if(picosatSolution == 'UNSAT'):
        return(picosatSolution)
    else:
        return(map(lambda atom: n2s(atom), picosatSolution))

def print_actions_in(clause):
    # Print all positive actions in clause.
    action_trace = []
    for c in clause:
        for a in actions:
            if (c.find(a) == 0):
                action_trace += [c]
    for a in action_trace[:-1]:
        print(a)

#################################################################
#
# Axioms about the world
#
#################################################################

actions = ['north', 'south', 'west', 'east', 'pick_up', 'drop']

# Movement axioms

def movement_axioms(t):
    """All movmement axioms for time t."""
    # Floor plane
    # Format: Location,
    #         Location North, Location East, Location South, Location West
    floorplan = [
          ['main_office',
           'mail_drop', 'main_office', 'main_office', 'main_office']
        , ['mail_drop',
           'mail_drop', 'ts', 'main_office', 'mail_drop']
        , ['ts',
           'ts', 'o101', 'ts', 'mail_drop']
        , ['o101',
           'o101', 'o103', 'r101', 'ts']
        , ['o103',
           'o103', 'o105', 'r103', 'o101']
        , ['o105',
           'o105', 'o107', 'r105', 'o103']
        , ['o107',
           'o107', 'o107', 'r107', 'o105']
        , ['r101',
           'o101', 'r101', 'r101', 'r101']
        , ['r103',
           'o103', 'r103', 'r103', 'r103']
        , ['r105',
           'o105', 'r105', 'r105', 'r105']
        , ['r107',
           'o107', 'r107', 'r107', 'r107']
        ]

    locations = [l[0] for l in floorplan]
    room_links = []
    # Movement axioms
    for l in floorplan:
        room = l[0]
        for (direction, connection) in zip(['north', 'east', 'south', 'west'],
                                           l[1:]):
            # room_t ∧ direction_t → connection_t+1
            room_links += [['~robot_at_%s_%d' % (room, t),
                            '~%s_%d' % (direction, t),
                            'robot_at_%s_%d' % (connection, t+1) ]]
    # Location does not change  if we do not move
    # robot_at_x ∧ ~north ∧ ~south ∧ ~west ∧ ~east → robot_at_x_t+1
    # = ¬robot_at_x ∨ north ∨ south ∨ west  ∨east ∨ robot_at_x_t+1
    no_move_no_location_change = []
    for l in locations:
        no_move_no_location_change += [['~robot_at_%s_%d' % (l, t),
                                            'north_%d' % t,
                                            'south_%d' % t,
                                            'west_%d' % t,
                                            'east_%d' % t,
                                            'robot_at_%s_%d' % (l, t+1)]]
    
    # There is only one robot
    # (¬ robot_at_main_office_t ∨ ¬ robot_at_mail_drop_t) ∧ 
    # (¬ robot_at_main_office_t ∨ ¬ robot_at_o101_t) ∧ 
    # (¬ robot_at_mail_drop_t ∨ ¬ robot_at_o101_t) ∧ 
    # ...
    only_one_robot = []
    for l0 in range(len(locations)):
        for l1 in range(l0+1, len(locations)):
            only_one_robot += [['~robot_at_%s_%d' % (locations[l0], t),
                                '~robot_at_%s_%d' % (locations[l1], t),]]

    # Exactly one action at a time:
    one_action_a_time = []
    # At least one action at a time
    # north_t ∨ south_t ∨ west_t ∨ east_t ∨ pick_up_t ∨ drop_t
    one_action_a_time += [['%s_%d' % (l, t) for l in actions]]
    # At most one action at a time
    for a0 in range(len(actions)):
        for a1 in range(a0+1, len(actions)):
            if (a0 != a1):
                one_action_a_time += [['~%s_%d' % (actions[a0], t),
                                       '~%s_%d' % (actions[a1], t)]]

    # Picking up and dropping mail
    pick_drop_mail = []
    # pick_up_t → robot_carries_mail_t+1
    pick_drop_mail += [['~pick_up_%d'  % t,
                        'robot_carries_mail_%d'  % (t+1)]]
    # drop_t → ¬ robot_carries_mail_t+1
    pick_drop_mail += [['~drop_%d' % t, '~robot_carries_mail_%d' % (t+1)]]
    # ¬ robot_carries_mail_t ∧ ¬ pick_up_t → ¬ robot_carries_mail_t+1
    pick_drop_mail += [['robot_carries_mail_%d' % t, 'pick_up_%d' % t,
                '~robot_carries_mail_%d' % (t+1)]]
    # robot_carries_mail_t ∧ ¬ drop_t → robot_carries_mail_t+1
    pick_drop_mail += [['~robot_carries_mail_%d' % t, 'drop_%d' % t,
                'robot_carries_mail_%d' % (t+1)]]

    # ¬(pick_up_t ∧
    #   ((robot_at_main_office_t ∧ ¬mail_at_main_office_t) ∨
    #    (robot_at_mail_drop_t ∧ ¬mail_at_mail_drop_t) ∨
    #    ...
    #   )
    #  )
    if True:
        for l in locations:
            pick_drop_mail += [['~pick_up_%d' % t,
                                'robot_at_%s_%d' % (l, t),
                                '~mail_at_%s_%d' % (l, t)]]

    # Moving mail
    move_mail = []
    for l in locations:
        # ¬ robot_carries_mail_t ∧ mail_at_l_t → mail_at_l_t+1
        move_mail += [['robot_carries_mail_%d' % t,
                       '~mail_at_%s_%d' % (l, t),
                       'mail_at_%s_%d' % (l, t+1)]]
        # robot_carries_mail_t ∧ robot_at_l_t+1 → mail_at_l_t+1
        move_mail += [['~robot_carries_mail_%d' % t,
                       '~robot_at_%s_%d' % (l, t+1), 'mail_at_%s_%d' % (l, t+1)]]


    # There is only one piece of mail
    # (¬ mail_at_main_office_t ∨ ¬ mail_at_mail_drop_t) ∧ 
    # (¬ mail_at_main_office_t ∨ ¬ mail_at_o101_t) ∧ 
    # (¬ mail_at_mail_drop_t ∨ ¬ mail_at_o101_t) ∧ 
    # ...
    one_piece_mail = []
    for l0 in range(len(locations)):
        for l1 in range(l0+1, len(locations)):
            one_piece_mail += [['~mail_at_%s_%d' % (locations[l0], t),
                                '~mail_at_%s_%d' % (locations[l1], t)]]

    # We're done
    return (room_links
            + no_move_no_location_change
            + only_one_robot
            + one_action_a_time
            + pick_drop_mail
            + move_mail
            + one_piece_mail
            )
    
#################################################################
#
# Reasoning about the world
#
#################################################################


t_max = 20
axioms_up_to_time_t = []
for t in range(0, t_max+1):
    axioms_up_to_time_t += movement_axioms(t)
    axioms = (axioms_up_to_time_t +
              [ # Start position of agent
                  ['robot_at_main_office_0']
                # Robot starts empty handed
                 , ['~robot_carries_mail_0']
                # Start position of mail
                 , ['mail_at_r107_0']
                # Target position for mail
                , ['mail_at_main_office_%d' % t]
                # , ['robot_at_ts_%d' % t]
                , ['~robot_carries_mail_%d' % t]
              ])
    solution = solve(axioms)
    if(solution != 'UNSAT'):
        print("Found a solution:")
        print_actions_in(solution)
        sys.exit(0)
print("Not possible in up to %d steps. :-(" % t_max)
