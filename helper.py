"""Break the Code Helper.

- A `tile` is a string of one number and one color (e.g., "2b").
- A `number` is the rank of a tile, from 0 to 9.
- A `color` is the color of a tile: "b" for black, "w" for white, and "g" for green.
- A `combination` is an array of tiles.

- A `ftile` (flattened tile) is numbered from 0 to 19, and that number holds both the rank and color
of the tile (e.g., "2b" would be "5").
- A `fcombination` is an array of ftiles.
"""


from typing import List, Tuple
import sys

import engine.board as bd
import engine.combination as cb
import engine.menu as mn


players = mn.ask_number_of_players()
fcombination = cb.combination_to_fcombination(mn.ask_user_combination(players))
board = bd.Board(fcombination, players)
hints = []  # type: List[Tuple[str, int]]
simulations = []  # type: List[Tuple[str, Tuple[float, float]]]
while True:
    choice = mn.display_main_menu(fcombination,
                                  board.get_central_fcombinations(),
                                  board.get_opponents_fcombinations(),
                                  hints,
                                  simulations)
    match choice:
        case 'h':
            hint = mn.display_hints_menu(players)
            if hint is not None:
                hint_name = hint[0]
                hint_results = []

                num_opponent_combs_before = [len(opponent_combs) for opponent_combs in board.get_opponents_fcombinations()]                                
                for opponent, hint_result in enumerate(hint[1]):
                    board.apply_hint(hint_name, hint_result, opponent)

                for opponent, hint_result in enumerate(hint[1]):
                    num_opponent_combs_after = len(board.get_opponent_fcombinations(opponent))
                    improvement = num_opponent_combs_before[opponent] - num_opponent_combs_after
                    hint_results.append((hint_result, improvement))

                hints.append((hint_name, hint_results))
                simulations = []
        case 's':
            hints_to_simulate = mn.display_simulation_menu(players)
            if hints_to_simulate is not None:
                for hint in hints_to_simulate:
                    if hint not in [simulation[0] for simulation in simulations]:
                        simulations.append((hint, board.simulate(hint)))
                simulations = sorted(simulations, key=lambda s: (round(s[1][0], 2), -s[1][1]), reverse=True)
        case 'c':
            opponent = mn.ask_opponent_number(players)
            if opponent == -1:
                mn.display_combinations_menu(board.get_central_fcombinations())
            else: 
                mn.display_combinations_menu(board.get_opponent_fcombinations(opponent))
        case 'u':
            if len(hints) > 0:
                hints.pop()
                simulations = []
            board = bd.Board(fcombination, players)
            for hint in hints:
                for opponent, res in enumerate(hint[1]):
                    board.apply_hint(hint[0], res[0], opponent)
        case 'q':
            really = input('Really quit? Press \'y\' to quit, anything else to go back: ')
            if really.lower() == 'y':
                sys.exit(0)
        case _:
            pass
