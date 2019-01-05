from utils import *
from structures.universal_element import *


class Grid:
    def __init__(self, nodes, elements, step):
        self.nodes = nodes
        self.elements = elements
        self.step = step

        self.H = [[0] * len(self.nodes) for i in range(len(self.nodes))]
        self.C = [[0] * len(self.nodes) for i in range(len(self.nodes))]
        self.P = [0] * len(self.nodes)

        self.temperatures = []

        self.initialize_universal_elements()
        self.map_matrices()

    def calculate(self, toprint):
        t0 = [node.t for node in self.nodes]
        self.temperatures.append(t0)
        cdtp = [
            x + p for p, x in zip(self.P, multiply_matrix_vector(self.CDT, t0))
        ]
        t1 = solve(self.HCT, cdtp)
        self.update_temperatures(t1)
        self.temperatures.append(t1)
        if toprint:
            # print(min(t1))
            print("Min: {}, Max: {}".format(min(t1), max(t1)))
        return t1

    def initialize_universal_elements(self):
        self.universal_elements = list()
        for element in self.elements:
            universal_element = UniversalElement(element)
            self.universal_elements.append(universal_element)

    def map_matrices(self):
        for element, universal_element in zip(self.elements, self.universal_elements):
            for i in range(4):
                self.P[element.nodes[i].id] += universal_element.P[i]
                for j in range(4):
                    self.H[element.nodes[i].id][element.nodes[j].id] += universal_element.H[i][j]
                    self.C[element.nodes[i].id][element.nodes[j].id] += universal_element.C[i][j]
        self.CDT = [
            [c / self.step for c in C] for C in self.C
        ]
        self.HCT = [
            [
                h + c for h, c in zip(H, CDT)
            ] for H, CDT in zip(self.H, self.CDT)
        ]
        self.t0 = [
            node.t for node in self.nodes
        ]

    def update_temperatures(self, t1):
        for node, t in zip(self.nodes, t1):
            node.t = t

