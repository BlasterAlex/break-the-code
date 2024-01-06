"""Board of the game."""


import copy
import itertools
import random
import statistics
from typing import List, Tuple
import combination as cb
import utils as ut


class Board:
    """Store information on possible opponent hands."""

    def __init__(self, combination: Tuple[str, ...], players: int = 2) -> None:
        """Generate initial opponent hands."""
        self._our_fcombination = cb.combination_to_fcombination(combination)
        # Generate the opponent fcombinations
        self._central_fcombinations = self._generate_fcombinations(players)
        self._opponents_fcombinations = [self.get_central_fcombinations() for _ in range(1, players)]

    def _generate_fcombinations(self, players: int = 2) -> List[Tuple[int, ...]]:
        """Generate all the possible fcombinations of the opponent."""
        positions = 5 if players < 4 else 4
        raw_fcombinations = list(itertools.combinations(list(i for i in range(20)), positions))
        filtered_fcombinations = []
        our_fives = self._our_fcombination.count(10) + self._our_fcombination.count(11)
        for fcombination in raw_fcombinations:
            # Remove a hand that has any of our tiles
            if len(set(self._our_fcombination).intersection(set(fcombination))) > 0:
                continue
            # If we have no 5 tiles, remove symmetric opponent hands with one 5 tile
            if our_fives == 0 and \
               fcombination.count(10) + fcombination.count(11) == 1 and \
               11 in fcombination:
                continue
            filtered_fcombinations.append(tuple(fcombination))

        return filtered_fcombinations

    def _filter_combinations(self,
                             fcombinations: List[Tuple[int, ...]],
                             hint: str,
                             answer: int | str | List[str]) -> List[Tuple[int, ...]]:
        """Return the filtered fcombinations after applying the given hint with its result."""
        return [fcombination for fcombination in fcombinations
                if ut.HINTS[hint]['function'](fcombination) == answer]

    def _filter_conflict_combinations(self,
                                      fcombinations: List[Tuple[int, ...]],
                                      target_fcombinations: List[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
        """Return the filtered fcombinations."""
        if len(target_fcombinations) == 0:
            return fcombinations
        
        matched_tiles = set.intersection(*[set(fcomb) for fcomb in target_fcombinations])
        if len(matched_tiles) == 0:
            return fcombinations
        
        filtered_fcombinations = []            
        for fcombination in fcombinations:
            ok = True
            for matched_tile in matched_tiles:
                if matched_tile in fcombination:
                    ok = False
                    break
            if ok:
                filtered_fcombinations.append(tuple(fcombination))
        
        return filtered_fcombinations

    def _try_to_apply_combination(self,
                                  combination: Tuple[int, ...],
                                  opponent: int = 0) -> bool:
        
        other_opponent_numbers = [num for num in range(len(self._opponents_fcombinations)) if num != opponent]
        other_opponent_combinations = [self.get_opponent_fcombinations(opponent_num) for opponent_num in other_opponent_numbers]
        filtered_opponent_combinations = [self._filter_conflict_combinations(opponent_combinations, [combination]) for opponent_combinations in other_opponent_combinations]

        if len(filtered_opponent_combinations) < 2:
            possible_opponent_combinations = filtered_opponent_combinations[0]
        else:
            possible_opponent_combinations = self._filter_conflict_combinations(filtered_opponent_combinations[0], filtered_opponent_combinations[1])
        
        return len(possible_opponent_combinations) > 0

    def get_central_fcombinations(self) -> List[Tuple[int, ...]]:
        """Return the possible central fcombinations."""
        return copy.deepcopy(self._central_fcombinations)
    
    def get_opponents_fcombinations(self) -> List[List[Tuple[int, ...]]]:
        """Return the possible opponents fcombinations."""
        return copy.deepcopy(self._opponents_fcombinations)

    def get_opponent_fcombinations(self, opponent: int = 0) -> List[Tuple[int, ...]]:
        """Return the possible fcombinations of the opponent."""
        return copy.deepcopy(self._opponents_fcombinations[opponent])

    def apply_hint(self, hint: str, answer: int | str | List[str], opponent: int = 0) -> None:
        """Apply a hint on the current board state."""
        opponent_fcombinations = self._filter_combinations(self._opponents_fcombinations[opponent],
                                                           hint,
                                                           answer)

        if len(self._opponents_fcombinations) > 1:
            filtered_fcombinations = []
            for opponent_fcombination in opponent_fcombinations:
                if self._try_to_apply_combination(opponent_fcombination, opponent):
                    filtered_fcombinations.append(opponent_fcombination)
            opponent_fcombinations = filtered_fcombinations

        for index, fcombinations in enumerate(self._opponents_fcombinations):
            if index == opponent:
                self._opponents_fcombinations[index] = opponent_fcombinations
            else:
                self._opponents_fcombinations[index] = self._filter_conflict_combinations(fcombinations,
                                                                                          opponent_fcombinations)

        if len(self._opponents_fcombinations) == 1:
            self._central_fcombinations = opponent_fcombinations
        else:
            for fcombinations in self._opponents_fcombinations:
                self._central_fcombinations = self._filter_conflict_combinations(self._central_fcombinations,
                                                                                fcombinations)

    def simulate(self, hint: str) -> Tuple[float, float]:
        """Return the average % of filtered combinations, and the standard deviation."""
        
        opponent_fcombinations = self.get_central_fcombinations()
        answers = [ut.HINTS[hint]['function'](fcombination) for fcombination in opponent_fcombinations]
        answers_count = {answer:answers.count(answer) for answer in answers}

        current_count = len(opponent_fcombinations)
        percentage_filtered = [(current_count - count) / current_count for _, count in answers_count.items()]
        stdev_filtered = 0 if len(percentage_filtered) < 2 else statistics.stdev(percentage_filtered) * 100
        return sum(percentage_filtered) / len(percentage_filtered), stdev_filtered
