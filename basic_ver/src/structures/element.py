from utils import *


class Node:
    def __init__(self, id, coord, t):
        self.id = id
        self.coord = coord
        self.t = t
        self.bc = False

    def show(self):
        print("Node: id({}), coord({}), temp({})".format(self.id, self.coord, self.t))


class Element:
    def __init__(self, nodes, K):
        self.nodes = nodes
        self.K = K

    def show(self):
        print("Element: k({})".format(self.K))
        for node in self.nodes:
            node.show()
        print("---------------------------------------")

