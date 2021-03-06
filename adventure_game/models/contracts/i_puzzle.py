from abc import ABCMeta, abstractmethod


class IPuzzle(metaclass=ABCMeta):
    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def required_items(self):
        pass

    @property
    @abstractmethod
    def takes_items(self):
        pass

    @property
    @abstractmethod
    def possible_answers(self):
        pass

    @property
    @abstractmethod
    def correct_answer(self):
        pass

    @property
    @abstractmethod
    def win_message(self):
        pass

    @property
    @abstractmethod
    def is_solved(self):
        pass

    @property
    @abstractmethod
    def reward(self):
        pass

    @property
    @abstractmethod
    def is_annoying(self):
        pass

    @abstractmethod
    def answer_is_correct(self, answer):
        pass
