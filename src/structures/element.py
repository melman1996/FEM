from utils import *


class Node:
    def __init__(self, id, coord, t, bc=False):
        self.id = id
        self.coord = coord
        self.t = t
        self.bc = bc

    def show(self):
        print("Node: id({}), coord({}), temp({})".format(self.id, self.coord, self.t))


class Element:
    def __init__(self, nodes, alfa, c, K, ro, tot=None):
        self.nodes = nodes
        self.alfa = alfa
        self.c = c
        self.K = K
        self.ro = ro
        self.tot = tot

    def show(self):
        print("Element: alfa({}), c({}), k({}), ro({})".format(self.alfa, self.c, self.K, self.ro))
        for node in self.nodes:
            node.show()
        print("---------------------------------------")
