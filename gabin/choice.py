from typing import List

from menuParser import MenuParser


class Choice:

    def __init__(self, ident: str, name: str, menuParser: MenuParser):
        self.ident = ident
        self.name = name
        self.menuParser = menuParser
        self.enabled = True
        self.yes = 0
        self.maybe = 0
        self.no = 0

    def getAsTuple(self) -> tuple:
        return (self.ident, self.name)

    def getMenu(self, nowDate) -> List[str]:
        return self.menuParser.getMenu(nowDate)

    def repeatMenu(self) -> List[str]:
        # get menu items without triggering the parser
        return self.menuParser.menu

    def getHasOpened(self) -> bool:
        return self.menuParser.open

    def countVotes(self, votes: dict):
        self.no, self.maybe, self.yes = 0, 0, 0
        for session, values in votes.items():
            for key, value in values.items():
                if key == self.ident:
                    if value == "0": self.no += 1
                    if value == "1": self.maybe += 1
                    if value == "2": self.yes += 1