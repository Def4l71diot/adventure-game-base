from abc import ABCMeta, abstractmethod


class IPuzzleFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_puzzle(self, puzzle_id, name, description, possible_answers, correct_answer, reward=None):
        pass