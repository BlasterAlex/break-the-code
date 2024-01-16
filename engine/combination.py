"""Transform combinations."""


from typing import Tuple
import engine.utils as ut


def combination_to_fcombination(combination: Tuple[str, ...]) -> Tuple[int, ...]:
    """Convert a combination to a fcombination."""
    fcombination = []
    # Add the non-5 tiles
    for tile in combination:
        if tile != '5g':
            fcombination.append(ut.TILES.index(tile))
    # Add the 5 tiles
    if combination.count('5g') == 1:
        fcombination.append(10)
    elif combination.count('5g') == 2:
        fcombination.extend([10, 11])
    return tuple(sorted(fcombination))


def fcombination_to_numbers(fcombination: Tuple[int, ...]) -> Tuple[int, ...]:
    """Return the ranks of the ftiles of a fcombination."""
    return tuple(ftile//2 for ftile in fcombination)


def fcombination_to_colors(fcombination: Tuple[int, ...]) -> Tuple[str, ...]:
    """Return the colors of the ftiles of a fcombination."""
    return tuple('b' if ftile in ut.BLACK_FTILES else
                 'w' if ftile in ut.WHITE_FTILES else
                 'g' for ftile in fcombination)


def fcombination_replace_five_tile(fcombination: Tuple[int, ...]) -> Tuple[int, ...]:
    """Return fcombination with 5 tile replaced by a paired tile."""
    if 10 in fcombination and 11 not in fcombination:
        f_list = list(fcombination)
        f_list[f_list.index(10)] = 11
        fcombination = tuple(f_list)
    return fcombination
