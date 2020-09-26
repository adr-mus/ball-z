import enum, abc

class Tile(abc.ABC):
    WIDTH = 2
    HEIGHT = 1

    def __init__(self):
        self.x = 0
        self.y = 0

    @abc.abstractmethod
    def on_hit(self, ball):
        pass


class BlankTile(Tile):
    def on_hit(self, ball):
        pass
    

class RegularTile(Tile):
    class Color(enum.Enum):
        RED = enum.auto()
        GREEN = enum.auto()
        YELLOW = enum.auto()
        BLUE = enum.auto()
        GREY = enum.auto()

    def __init__(self):
        self.color = self.Color.RED
        Tile.__init__(self)
    

class InvisibleTile(Tile):
    def __init__(self):
        self.hit = False
        Tile.__init__(self)


class Brick(Tile):
    def __init__(self):
        self.hit = False
        Tile.__init__(self)


class TripleTile(Tile):
    def __init__(self):
        self.n_hits = 0
        Tile.__init__(self)

class ExplosiveTile(Tile):
    pass