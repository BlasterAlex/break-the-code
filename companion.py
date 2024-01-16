"""Break the Code Companion."""


from typing import List, Tuple, Set
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

MAIN_MENU = """(a) Ask a question
(c) Check the tiles
(u) Undo (cancel last move)
(q) Quit
"""

HUMAN_COLOR = '\x1b[0;30;42m'
BOT_COLOR = '\x1b[0;30;46m'
HUMAN_ICON = '🧑'
BOT_ICON = '🤖'

WINNING_MOVE = '✅ Win'
LOSING_MOVE = '❌ Lose'
ENDING_MOVES = (WINNING_MOVE, LOSING_MOVE)


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
                            fcombination = cb.fcombination_replace_five_tile(fcombination)
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
                       bot_players: Tuple[int, ...],
                       bot_games: List[bd.Board],
                       hint: str,
                       results: List[Tuple[int, int | str | Tuple[str, ...]]]) -> None:
    """Apply hint results to bot games."""
    if hint in ENDING_MOVES:
        return
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
                      people: int,
                      player_names: Tuple[str, ...],
                      history: List[Tuple[int, str, List[Tuple[int, int | str | Tuple[str, ...]]]]]) -> str:
    """Display the main menu and return a valid user choice."""
    choice = None
    while True:
        mn.clear_screen()
        print(TITLE)
        print(f'{players}-player game')
        print(f'{HUMAN_COLOR + HUMAN_ICON + ut.END_COLOR}: {people}',
              f'{BOT_COLOR + BOT_ICON + ut.END_COLOR}: {players - people}')

        if len(history) == 0:
            print('\nNo moves yet')
        else:
            print('\nMove history:')
            max_width = max(len(player_names[h[0]]) for h in history)
            for hint in history:
                player, hint_name, results = hint
                hint_results = [f'{player_names[p]} {mn.hint_result_as_str(r)}' for p, r in results]
                if hint_name in ENDING_MOVES:
                    move_results = ', '.join([hint_name] + hint_results)
                else:
                    move_results = ut.HINTS[hint_name]['description'] + ': ' + ', '.join(hint_results)
                print(f'- {player_names[player].ljust(max_width)} ' + move_results)

        print('\nOptions:')
        print(MAIN_MENU)

        if choice is not None:
            print(f'Error: There is no \'{choice}\' option')
        choice = input('Choose option: ')
        if choice in ('a', 'c', 'u', 'q'):
            break

    return choice


def display_players_menu(player_names: Tuple[str, ...],
                         out_of_the_game: Set[int]) -> int | None:
    """Display the player selection menu and return the player number."""   
    mn.clear_screen()
    print(TITLE)
    print('Select player whose turn it is:')

    players_in_game = []
    for player, name in enumerate(player_names):
        if player not in out_of_the_game:
            players_in_game.append(player)
            option_num = len(players_in_game)
            print(f'({option_num}) {name}')
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

        if not 0 < choice <= len(players_in_game):
            print('Error: Enter the correct player')
            continue
        
        return players_in_game[choice-1]


def display_player_hints_menu(players: int = 2) -> str | None:
    """Display the player hints menu and return a valid hint."""
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


def display_combinations_menu(player_names: Tuple[str, ...],
                              human_players: Tuple[int, ...],
                              bot_players: Tuple[int, ...],
                              central_fcombination: Tuple[int, ...],
                              people_fcombinations: List[Tuple[int, ...]],
                              bot_fcombinations: List[Tuple[int, ...]]) -> None:
    """Display the combinations menu."""
    mn.clear_screen()
    print(TITLE)

    players = len(player_names)
    if players == 2:
        fcombination = cb.combination_to_fcombination(mn.ask_user_combination(
            players,
            prompt='Enter your guess, separated by spaces'))

        # Case central combination has one 5 tile
        if 11 in central_fcombination and 10 not in central_fcombination:
            fcombination = cb.fcombination_replace_five_tile(fcombination)

        if fcombination == central_fcombination:
            print('✅ You\'re correct')
        else:
            print('❌ You\'re wrong')
    else:
        print('Central tiles:')
        print(mn.ftiles_as_colored_tiles(central_fcombination))

        print('\nPlayer tiles:')
        for player, name in enumerate(player_names):
            print(name + ': ', end='')
            if player in human_players:
                print(mn.ftiles_as_colored_tiles(
                    people_fcombinations[human_players.index(player)]))
            elif player in bot_players:
                print(mn.ftiles_as_colored_tiles(
                    bot_fcombinations[bot_players.index(player)]))

    input('\nPress \'[Enter]\' to go back.')


def bot_makes_a_move(bot_games: List[bd.Board],
                     bot_players: Tuple[int, ...],
                     winning_players: Set[int]) -> str | None:
    """The bot player takes a turn and returns the chosen hint."""
    hint = None
    bot_game = bot_games[bot_players.index(player)]
    if len(bot_game.get_central_fcombinations()) == 1:
        hint = WINNING_MOVE
    elif len(winning_players) > 0:
        hint = LOSING_MOVE
    else:
        bot_hints = display_bot_hints_menu(players)
        if bot_hints is None:
            return None
        if len(bot_hints) > 0:
            if len(bot_hints) == 1:
                hint = bot_hints[0]
            else:
                sim = [(hint, bot_game.simulate(hint)) for hint in bot_hints]
                sim = sorted(sim, key=lambda s: (round(s[1][0], 2), -s[1][1]), reverse=True)
                hint = sim[0][0]
    return hint


players = mn.ask_number_of_players()
people = ask_number_of_people(players)
people_fcombinations = ask_player_fcombinations(players, people)
central_fcombination, bot_fcombinations = distribute_remaining_tiles(
    players, people_fcombinations)

human_players = tuple(range(people))
bot_players = tuple(range(len(human_players), players))
player_names = \
    tuple(HUMAN_COLOR + (f'{p+1}' if len(human_players) > 1 else '') +
          HUMAN_ICON + ut.END_COLOR for p in range(len(human_players))) + \
    tuple(BOT_COLOR + (f'{b+1}' if len(bot_players) > 1 else '') +
          BOT_ICON + ut.END_COLOR for b in range(len(bot_players)))

history = []
bot_games = [bd.Board(fc, players) for fc in bot_fcombinations]

while True:
    choice = display_main_menu(players, people, player_names, history)
    match choice:
        case 'a':
            # Getting information from move history
            out, win = [], []
            for h in history:
                player, hint_name, results = h
                if hint_name in ENDING_MOVES:
                    out.append(player)
                    if hint_name == WINNING_MOVE:
                        win.append(player)
                        out.extend([p for p, r in results if r in ENDING_MOVES])
            out_of_the_game, winning_players = set(out), set(win)

            # Getting the number of player whose turn it is
            player = display_players_menu(player_names, out_of_the_game)
            if player is None:
                continue
            
            # Player makes a move
            hint = None
            if player in human_players:
                hint = display_player_hints_menu(players)
            elif player in bot_players:
                hint = bot_makes_a_move(bot_games, bot_players, winning_players)
            if hint is None:
                continue

            # Player is out of the game
            if hint in ENDING_MOVES:
                losers = []
                if hint == WINNING_MOVE:
                    order = [h[0] for h in history]
                    player_order = tuple(sorted(set(order), key=order.index))
                    for bot in bot_players:
                        if player_order.index(bot) >= player_order.index(player):
                            break
                        if bot not in out_of_the_game:
                            losers.append((bot, LOSING_MOVE))
                history.append((player, hint, losers))
                continue

            # Getting results of the selected hint
            results = []
            for index, fcomb in enumerate(people_fcombinations):
                opponent = human_players[index]
                if players == 4 or opponent != player:
                    results.append((opponent, ut.HINTS[hint]['function'](fcomb)))
            for index, fcomb in enumerate(bot_fcombinations):
                bot = bot_players[index]
                if players == 4 or bot != player:
                    results.append((bot, ut.HINTS[hint]['function'](fcomb)))

            # Applying and saving hint results
            apply_hint_to_bots(players, bot_players, bot_games, hint, results)
            history.append((player, hint, results))
        case 'c':
            display_combinations_menu(player_names,
                                      human_players,
                                      bot_players,
                                      central_fcombination,
                                      people_fcombinations,
                                      bot_fcombinations)
        case 'u':
            if len(history) > 0:
                history.pop()
                bot_games = [bd.Board(fc, players) for fc in bot_fcombinations]
                for hint in history:
                    apply_hint_to_bots(players, bot_players, bot_games, hint[1], hint[2])
        case 'q':
            really = input('Really quit? Press \'y\' to quit, anything else to go back: ')
            if really.lower() == 'y':
                sys.exit(0)
        case _:
            pass
