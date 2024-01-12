"""Break the Code Companion."""


from typing import List, Tuple
import itertools
import random
import sys

import engine.combination as cb
import engine.menu as mn
import engine.utils as ut
import engine.board as bd


TITLE = """================================
=== Break the Code Companion ===
================================
"""

MAIN_MENU = """(h) Add hint
(u) Undo (remove last hint)
(c) Check combination
(q) Quit
"""

HUMAN_COLOR = '\x1b[0;30;42m'
BOT_COLOR = '\x1b[0;30;46m'
HUMAN_ICON = '🧑'
BOT_ICON = '🤖'

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


def apply_hint_to_bots(players: int,
                       bot_players: Tuple[int],
                       bot_games: List[bd.Board],
                       hint: str,
                       results: Tuple[int, int | str | Tuple[str, ...]]) -> None:
    """Apply hint results to bot games."""
    for index, board in enumerate(bot_games):
        bot = bot_players[index]
        other_players = [p for p in range(players) if p != bot]
        for result in results:
            player, answer = result
            if player != bot:
                opponent = other_players.index(player)
                board.apply_hint(hint, answer, opponent)
        bot_games[index] = board


def display_main_menu(players: int,
                      player_names: Tuple[str],
                      bot_games: List[bd.Board],
                      bot_fcombinations: List[Tuple[int, ...]],
                      hints: List[Tuple[str, List[Tuple[int, int | str | Tuple[str, ...]]]]]) -> str:
    """Display the main menu and return a valid user choice."""
    choice = None
    while True:
        mn.clear_screen()
        print(TITLE)
        print(f'{players}-player game')
        print(f'{HUMAN_COLOR + HUMAN_ICON + ut.END_COLOR}: {players-len(bot_fcombinations)}',
              f'{BOT_COLOR + BOT_ICON + ut.END_COLOR}: {len(bot_fcombinations)}')

        print()
        for index, bot_game in enumerate(bot_games):
            print(f'Bot {index+1} combinations: {len(bot_game.get_central_fcombinations())}')

        if len(hints) == 0:
            print('\nNo hints yet')
        else:
            print('\nCurrent hints:')
            for hint in hints:
                results = ', '.join(f'{player_names[p]} {mn.hint_result_as_str(r)}' for p, r in hint[1])
                print('- ' + ut.HINTS[hint[0]]['description'] + f': {results}')

        print('\nOptions:')
        print(MAIN_MENU)

        if choice is not None:
            print(f'Error: There is no \'{choice}\' option')
        choice = input('Choose option: ')
        if choice in ('h', 'u', 'c', 'q'):
            break

    return choice


def display_player_menu(player_names: Tuple[str]) -> int | None:
    """Display the player selection menu."""
    mn.clear_screen()
    print(TITLE)
    print('Select player whose turn it is:')
    for player, name in enumerate(player_names):
        print(f'({player+1}) {name}')
    print('(q) Go back\n')

    while True:    
        choice = input('Choose player: ')
        if choice == 'q':
            return None

        try:
            choice = int(choice)
        except ValueError:
            print(f'Error: Value \'{choice}\' must be an integer')
            continue

        if not 0 < choice <= len(player_names):
            print('Error: Enter the correct player number')
            continue
        
        return choice-1


def display_opponent_hints_menu(players: int = 2) -> str | None:
    """Display the opponent hints menu and return a valid hint."""
    choice = None
    while True:
        mn.clear_screen()
        print(TITLE)
        print(mn.get_hint_shortcuts(players))

        if choice is not None:
            print(f'Error: The hint \'{choice}\' is not valid')
        choice = input('Choose option: ')
        if choice == 'q':
            return None
        if choice in ut.HINTS:
            return choice


def display_bot_hints_menu(players: int = 2) -> Tuple[str, ...] | None:
    """Display the bot hints menu and return a valid hint."""
    wrong_hint = None
    while True:
        mn.clear_screen()
        print(TITLE)
        print(mn.get_hint_shortcuts(players))

        if wrong_hint is not None:
            print(f'Error: The hint \'{wrong_hint}\' is not a valid hint')
        choice = input('Enter the hints available for selection, separated by spaces (e.g., st tw nc): ')
        if choice == 'q':
            return None

        hints = choice.split()
        for hint in hints:
            if hint not in ut.HINTS:
                wrong_hint = hint
                break
        else:
            return tuple(hints)


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

human_players = tuple(range(people))
bot_players = tuple(range(len(human_players), players))
player_names = tuple(HUMAN_COLOR + (f'{p+1}' if len(human_players) > 1 else '') + HUMAN_ICON + ut.END_COLOR for p in range(len(human_players))) + \
    tuple(BOT_COLOR + (f'{b+1}' if len(bot_players) > 1 else '') + BOT_ICON + ut.END_COLOR for b in range(len(bot_players)))

people_fcombinations = ask_player_fcombinations(players, people)
central_fcombination, bot_fcombinations = distribute_remaining_tiles(
    players, people_fcombinations)

hints = []
bot_games = [bd.Board(fc, players) for fc in bot_fcombinations]

while True:
    choice = display_main_menu(players,
                               player_names,
                               bot_games,
                               bot_fcombinations,
                               hints)
    match choice:
        case 'h':
            player = display_player_menu(player_names)
            if player is None:
                continue
            
            hint = None
            if player in human_players:
                hint = display_opponent_hints_menu(players)
            elif player in bot_players:
                bot_hints = display_bot_hints_menu(players)
                if bot_hints is not None:
                    bot_game = bot_games[bot_players.index(player)]
                    simulations = [(hint, bot_game.simulate(hint)) for hint in bot_hints]
                    simulations = sorted(simulations, key=lambda s: (round(s[1][0], 2), -s[1][1]), reverse=True)
                    hint = simulations[0][0]

            if hint is not None:
                results = []
                for index, fcomb in enumerate(people_fcombinations):
                    opponent = human_players[index]
                    if players == 4 or opponent != player:
                        results.append((opponent, ut.HINTS[hint]['function'](fcomb)))
                for index, fcomb in enumerate(bot_fcombinations):
                    bot = bot_players[index]
                    if players == 4 or bot != player:
                        results.append((bot, ut.HINTS[hint]['function'](fcomb)))
                apply_hint_to_bots(players, bot_players, bot_games, hint, results)
                hints.append((hint, results))
        case 'u':
            if len(hints) > 0:
                hints.pop()
            bot_games = [bd.Board(fc, players) for fc in bot_fcombinations]
            for hint in hints:
                apply_hint_to_bots(players, bot_players, bot_games, hint[0], hint[1])
        case 'c':
            display_combinations_menu(players, central_fcombination, bot_fcombinations)
        case 'q':
            really = input('Really quit? Press \'y\' to quit, anything else to go back: ')
            if really.lower() == 'y':
                sys.exit(0)
        case _:
            pass