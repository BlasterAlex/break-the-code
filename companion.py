"""Break the Code Companion."""

from typing import List, Tuple
import itertools
import random
import sys

import combination as cb
import menu as mn
import utils as ut

TITLE = """================================
=== Break the Code Companion ===
================================
"""

MAIN_MENU = """(h) Add hint
(u) Undo (remove last hint)
(c) Check combination
(q) Quit
"""

def ask_number_of_people(players: int = 2) -> int:
    """Ask the user for the number of people in game and return it."""
    if players == 2:
        return 1

    while True:
        choice = input('Enter number of people: ')
        try:
            people = int(choice)
        except ValueError:
            print(f'Error: Value \'{choice}\' must be an integer')
            continue
        
        if people >= players:
            people = players-1
        elif people < 1:
            people = 1
        return people


def ask_player_fcombinations(players: int = 2, people: int = 1) -> List[Tuple[int, ...]]:
    """Ask players for their tiles and return them."""
    fcombinations = []
    
    for player in range(people):
        mn.clear_screen()
        print(TITLE)
        print(f'Player #{player+1}')
        while True:
            fcombination = cb.combination_to_fcombination(mn.ask_user_combination(players))

            if len(fcombinations) > 0:
                # Case two players have the 5 tiles
                if 10 in fcombination and 11 not in fcombination:
                    for fcomb in fcombinations:
                        if 10 in fcomb:
                            f_list = list(fcombination)
                            f_list[f_list.index(10)] = 11
                            fcombination = tuple(f_list)
                            break

                fcomb_intersections = set.intersection(
                    set(itertools.chain(*fcombinations)), set(fcombination))
                if len(fcomb_intersections) > 0:
                    print('Error: Check the tiles entered')
                    continue

            fcombinations.append(fcombination)
            break

    return fcombinations


def distribute_remaining_tiles(players: int,
                               people_fcombinations: List[Tuple[int, ...]]) -> Tuple[Tuple[int, ...], List[Tuple[int, ...]]]:
    """Distribute the remaining tiles among bots in game."""
    bots = players - len(people_fcombinations)
    remaining = list(set(range(20)) -
                     set(itertools.chain(*people_fcombinations)))
    random.shuffle(remaining)

    positions = 5 if players < 4 else 4
    fcombs = [tuple(sorted(remaining[i:i+positions])) for i in range(0, len(remaining), positions)]
    
    if players == 2:
        return (fcombs[0], fcombs[:1])
    return (fcombs[0], fcombs[1:bots+1])


def display_main_menu(players: int,
                      bot_fcombinations: List[Tuple[int, ...]],
                      hints: List[Tuple[str, List[int | str | Tuple[str, ...]]]]) -> str:
    """Display the main menu and return a valid user choice."""
    choice = None
    while True:
        mn.clear_screen()
        print(TITLE)
        print('Players in game:', players)
        print('Bots in game:', len(bot_fcombinations))

        if len(hints) == 0:
            print('\nNo hints yet')
        else:
            print('\nCurrent hints:')
            for hint in hints:
                results = ', '.join(mn.hint_result_as_str(r) for r in hint[1])
                print('- ' + ut.HINTS[hint[0]]['description'] + f': {results}')

        print('\nOptions:')
        print(MAIN_MENU)

        if choice is not None:
            print(f'Error: There is no \'{choice}\' option')
        choice = input('Choose option: ')
        if choice in ('h', 'u', 'c', 'q'):
            break

    return choice


def display_hints_menu(players: int = 2) -> str | None:
    """Display the hints menu and return a valid hint"""
    choice = None

    while True:
        mn.clear_screen()
        print(TITLE)
        print(mn.get_hint_shortcuts(players))

        if choice is not None:
            print(f'Error: The hint \'{choice}\' is not valid')
        choice = input('Choose option: ')
        if choice in ut.HINTS or choice == 'q':
            break

    return choice


def display_combinations_menu(players: int,
                              central_fcombination: Tuple[int, ...],
                              bot_fcombinations: List[Tuple[int, ...]]) -> None:
    """Display the combinations menu."""
    mn.clear_screen()
    print(TITLE)

    if players == 2:
        fcombination = cb.combination_to_fcombination(mn.ask_user_combination(
            players,
            prompt='Enter your answer, separated by spaces'))

        # Case central combination has one 5 tile
        if 11 in central_fcombination and 10 not in central_fcombination:
            if 10 in fcombination and 11 not in fcombination:
                f_list = list(fcombination)
                f_list[f_list.index(10)] = 11
                fcombination = tuple(f_list)

        if fcombination == central_fcombination:
            print('✅ You\'re correct')
        else:
            print('❌ You\'re wrong')
    else:
        print('Central tiles:')
        print(mn.ftiles_as_colored_tiles(central_fcombination))

        print('\nBot tiles:')
        for bot, fcomb in enumerate(bot_fcombinations):
            print(f'#{bot+1}: ', end='')
            print(mn.ftiles_as_colored_tiles(fcomb))

    input('\nPress \'[Enter]\' to go back.')


players = mn.ask_number_of_players()
people = ask_number_of_people(players)

people_fcombinations = ask_player_fcombinations(players, people)
central_fcombination, bot_fcombinations = distribute_remaining_tiles(
    players, people_fcombinations)

hints = []

while True:
    choice = display_main_menu(players,
                               bot_fcombinations,
                               hints)
    match choice:
        case 'h':
            hint = display_hints_menu(players)
            if hint is not None:
                results = [ut.HINTS[hint]['function'](fcomb) for fcomb in bot_fcombinations]
                hints.append((hint, results))
        case 'u':
            if len(hints) > 0:
                hints.pop()
        case 'c':
            display_combinations_menu(players, central_fcombination, bot_fcombinations)
        case 'q':
            really = input('Really quit? Press \'y\' to quit, anything else to go back: ')
            if really.lower() == 'y':
                sys.exit(0)
        case _:
            pass