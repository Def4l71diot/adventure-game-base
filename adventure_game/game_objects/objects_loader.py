from adventure_game.contracts import IObjectsLoader
from adventure_game.factories.contracts import *
from adventure_game.models import Room, Puzzle
from bs4 import BeautifulSoup
from lxml import etree


class ObjectsLoader(IObjectsLoader):
    def __init__(self,
                 item_factory: IItemFactory,
                 puzzle_factory: IPuzzleFactory,
                 room_factory: IRoomFactory,
                 player_factory: IPlayerFactory,
                 xml_data_file_name):
        self.raw_items = {}
        self.raw_puzzles = {}
        self.raw_rooms = {}
        self.raw_player = {}
        self.item_factory = item_factory
        self.puzzle_factory = puzzle_factory
        self.room_factory = room_factory
        self.player_factory = player_factory
        self.items_as_objects = {}
        self.puzzles_as_objects = {}
        self.rooms_as_objects = {}
        self.player_as_object = None
        self.xml_data_file_name = xml_data_file_name

    def load(self):
        self._parse_xml(self.xml_data_file_name)
        self.load_custom_objects()
        self.convert_objects()

        return [self.items_as_objects,
                self.puzzles_as_objects,
                self.rooms_as_objects,
                self.player_as_object]

    def reload(self):
        self.items_as_objects = {}
        self.puzzles_as_objects = {}
        self.rooms_as_objects = {}
        self.player_as_object = None
        self.load_custom_objects()
        self.convert_objects()

        return [self.items_as_objects,
                self.puzzles_as_objects,
                self.rooms_as_objects,
                self.player_as_object]

    # reference - adapted from:
    # https://stackoverflow.com/questions/34554856/python-instantiate-all-classes-within-a-module Jan 1 '16 at 9:03
    # Creates a new instance of all subclasses of a class
    def load_custom_objects(self):
        custom_puzzles = [puzzle_obj() for puzzle_obj in Puzzle.__subclasses__()]
        custom_rooms = [room_obj() for room_obj in Room.__subclasses__()]

        for puzzle in custom_puzzles:
            self.puzzles_as_objects[puzzle.id] = puzzle

        for room in custom_rooms:
            self.rooms_as_objects[room.id] = room

    # end reference

    def convert_objects(self):
        self.convert_items()
        self.convert_puzzles()
        self.convert_rooms()
        self.convert_player()

    def convert_items(self):
        for item_id in self.raw_items:
            item_object = self.item_factory.create_item(item_id,
                                                        self.raw_items[item_id]["name"],
                                                        self.raw_items[item_id]["description"])
            self.items_as_objects[item_id] = item_object

    def convert_puzzles(self):
        for puzzle_id in self.raw_puzzles:
            is_custom_puzzle = puzzle_id in self.puzzles_as_objects
            puzzle_name = self.raw_puzzles[puzzle_id]["name"]
            puzzle_description = self.raw_puzzles[puzzle_id]["description"]
            puzzle_possible_answers = self.raw_puzzles[puzzle_id]["possible_answers"]
            puzzle_correct_answer = self.raw_puzzles[puzzle_id]["correct_answer"]
            puzzle_win_message = self.raw_puzzles[puzzle_id]["win_message"]
            reward_item_id = self.raw_puzzles[puzzle_id]["reward_item_id"]
            reward_item = self.items_as_objects[reward_item_id] if reward_item_id else None

            puzzle_required_items = []
            for required_item_id in self.raw_puzzles[puzzle_id]["required_items_ids"]:
                puzzle_required_items.append(self.items_as_objects[required_item_id])

            puzzle_takes_items = self.raw_puzzles[puzzle_id]["takes_items"]
            puzzle_is_annoying = self.raw_puzzles[puzzle_id]["is_annoying"]

            if is_custom_puzzle:
                puzzle = self.puzzles_as_objects[puzzle_id]
                puzzle._name = puzzle_name
                puzzle._description = puzzle_description
                puzzle._possible_answers = puzzle_possible_answers
                puzzle._correct_answer = puzzle_correct_answer
                puzzle._win_message = puzzle_win_message
                puzzle._reward = reward_item
                puzzle._required_items = puzzle_required_items
                puzzle._takes_items = puzzle_takes_items
                puzzle._is_annoying = puzzle_is_annoying
            else:
                puzzle = self.puzzle_factory.create_puzzle(puzzle_id,
                                                           puzzle_name,
                                                           puzzle_description,
                                                           puzzle_possible_answers,
                                                           puzzle_correct_answer,
                                                           win_message=puzzle_win_message,
                                                           reward=reward_item,
                                                           required_items=puzzle_required_items,
                                                           takes_items=puzzle_takes_items,
                                                           is_annoying=puzzle_is_annoying)

            self.puzzles_as_objects[puzzle_id] = puzzle

    def convert_rooms(self):
        for room_id in self.raw_rooms:
            is_custom_room = room_id in self.rooms_as_objects
            room_name = self.raw_rooms[room_id]["name"]
            room_description = self.raw_rooms[room_id]["description"]
            room_exits = self.raw_rooms[room_id]["exits"]

            room_items = []
            for item_id in self.raw_rooms[room_id]["room_item_ids"]:
                room_items.append(self.items_as_objects[item_id])

            room_puzzles = []
            for puzzle_id in self.raw_rooms[room_id]["room_puzzles_ids"]:
                room_puzzles.append(self.puzzles_as_objects[puzzle_id])

            if is_custom_room:
                room = self.rooms_as_objects[room_id]
                room._name = room_name
                room._description = room_description
                room._exits = room_exits
                room._items = room_items
                room._puzzles = room_puzzles
            else:
                room = self.room_factory.create_room(room_id,
                                                     room_name,
                                                     room_description,
                                                     exits=room_exits,
                                                     items=room_items,
                                                     puzzles=room_puzzles)

            self.rooms_as_objects[room_id] = room

    def convert_player(self):
        player_inventory = []
        for item_id in self.raw_player["inventory"]:
            player_inventory.append(self.items_as_objects[item_id])

        player_location = self.rooms_as_objects[self.raw_player["location"]]

        self.player_as_object = self.player_factory.create_player(self.raw_player["name"],
                                                                  player_location,
                                                                  inventory=player_inventory)

    def _parse_xml(self, file_name):
        raw_xml = etree.parse(file_name)
        raw_xml.xinclude()
        xml = BeautifulSoup(etree.tostring(raw_xml), "xml")

        items = xml.data.items.find_all("item")
        for item in items:
            item_id = item["id"]
            item_name = item.find('name').string
            item_desc = item.description.string
            self.raw_items[item_id] = {"name": item_name, "description": item_desc}

        puzzles = xml.data.puzzles.find_all("puzzle")
        for puzzle in puzzles:
            puzzle_id = puzzle["id"]
            puzzle_name = puzzle.find("name").string
            puzzle_desc = puzzle.description.string
            correct_answer = puzzle.correct_answer.string
            win_message = puzzle.win_message.string if puzzle.win_message else None
            reward_item_id = puzzle.reward_item_id.string if puzzle.reward_item_id else None
            possible_answers_elements = puzzle.possible_answers.find_all("answer")
            possible_answers = []
            for answer_element in possible_answers_elements:
                possible_answers.append(answer_element.string)

            required_items_elements = puzzle.required_items.find_all("item") if puzzle.required_items else []
            required_items = []
            for required_item_element in required_items_elements:
                required_items.append(required_item_element.string)

            takes_items = puzzle.has_attr("takes_items")
            is_annoying = puzzle.has_attr("is_annoying")

            self.raw_puzzles[puzzle_id] = {"name": puzzle_name,
                                           "description": puzzle_desc,
                                           "possible_answers": possible_answers,
                                           "correct_answer": correct_answer,
                                           "win_message": win_message,
                                           "reward_item_id": reward_item_id,
                                           "required_items_ids": required_items,
                                           "takes_items": takes_items,
                                           "is_annoying": is_annoying}

        rooms = xml.data.rooms.find_all("room")
        for room in rooms:
            room_id = room["id"]
            room_name = room.find("name").string
            room_desc = room.description.string

            room_items_elements = room.items.find_all("item") if room.items else []
            room_items = []
            for room_item_element in room_items_elements:
                room_items.append(room_item_element.string)

            room_puzzles_elements = room.puzzles.find_all("puzzle") if room.puzzles else []
            room_puzzles = []
            for room_puzzle_element in room_puzzles_elements:
                room_puzzles.append(room_puzzle_element.string)

            room_exits_elements = room.exits.children
            room_exits = {}
            for room_exit in room_exits_elements:
                if not room_exit.name:
                    continue
                room_exits[room_exit.name] = room_exit.string

            self.raw_rooms[room_id] = {"name": room_name,
                                       "description": room_desc,
                                       "room_item_ids": room_items,
                                       "room_puzzles_ids": room_puzzles,
                                       "exits": room_exits}

        player = xml.data.find("player")
        player_name = player.find("name").string
        player_location_room_id = player.location.string
        player_inventory_raw = player.inventory.find_all("item")
        player_inventory_item_ids = []
        for player_inventory_item_id in player_inventory_raw:
            player_inventory_item_ids.append(player_inventory_item_id.string)

        self.raw_player = {"name": player_name,
                           "location": player_location_room_id,
                           "inventory": player_inventory_item_ids}
