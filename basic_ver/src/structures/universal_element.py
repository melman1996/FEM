from utils import *

from math import sqrt
from operator import add


class UniversalElement:
    def __init__(self, element, ro, c, alfa, tot):
        self.element = element
        self.p = [
            (-1 / sqrt(3), -1 / sqrt(3)),
            (1 / sqrt(3), -1 / sqrt(3)),
            (1 / sqrt(3), 1 / sqrt(3)),
            (-1 / sqrt(3), 1 / sqrt(3))
        ]
        self.ro = ro
        self.c = c
        self.alfa = alfa
        self.tot = tot
        self.length = [0, 0, 0, 0]

        self.detJ = []
        self.dNdX = []
        self.dNdY = []

        self.P = []
        self.H = []
        self.C = []

        self.generate_matrix_J()
        self.generate_matrix_H()
        self.generate_matrix_C()
        self.generate_matrix_bc_H()
        self.generate_vector_P()

    def generate_matrix_J(self):
        dndksi = dNdKsi()
        pdNdKsi = [
            [dndksi[i](*point) for point in self.p] for i in range(4)
        ]
        dndeta = dNdEta()
        pdNdEta = [
            [dndeta[i](*point) for point in self.p] for i in range(4)
        ]
        dKsi = [
            [
                sum([
                    self.element.nodes[i].coord[k] * pdNdKsi[i][j] for i in range(4)
                ]) for j in range(4)
            ] for k in range(2)
        ]
        dEta = [
            [
                sum([
                    self.element.nodes[i].coord[k] * pdNdEta[i][j] for i in range(4)
                ]) for j in range(4)
            ] for k in range(2)
        ]
        jxx = dKsi + dEta
        self.detJ = [
            jxx[0][i] * jxx[3][i] - jxx[1][i] * jxx[2][i] for i in range(4)
        ]
        jxxx = [
            [jxx[3][i] / self.detJ[i] for i in range(4)],
            [-jxx[1][i] / self.detJ[i] for i in range(4)],
            [jxx[2][i] / self.detJ[i] for i in range(4)],
            [jxx[0][i] / self.detJ[i] for i in range(4)]
        ]
        self.dNdX = [
            [
                jxxx[0][j] * pdNdKsi[i][j] + jxxx[1][j] * pdNdEta[i][j] for i in range(4)
            ] for j in range(4)
        ]
        self.dNdY = [
            [
                jxxx[2][j] * pdNdKsi[i][j] + jxxx[3][j] * pdNdEta[i][j] for i in range(4)
            ] for j in range(4)
        ]

    def generate_matrix_H(self):
        dNdXdNdXTDetJ = [
            [
                [
                    self.dNdX[k][i] * self.dNdX[k][j] * self.detJ[k] for i in range(4)
                ] for j in range(4)
            ] for k in range(4)
        ]
        dNdYdNdYTDetJ = [
            [
                [
                    self.dNdY[k][i] * self.dNdY[k][j] * self.detJ[k] for i in range(4)
                ] for j in range(4)
            ] for k in range(4)
        ]
        Ktimes = [
            [
                [
                    self.element.K * (dNdXdNdXTDetJ[k][j][i] + dNdYdNdYTDetJ[k][j][i]) for i in range(4)
                ] for j in range(4)
            ] for k in range(4)
        ]
        self.H = [
            [
                Ktimes[0][j][i] + Ktimes[1][j][i] + Ktimes[2][j][i] + Ktimes[3][j][i] for i in range(4)
            ] for j in range(4)
        ]

    def generate_matrix_C(self):
        n = N()
        Np = [
            [
                n[i](*point) for i in range(4)
            ] for point in self.p
        ]
        tmp = [
            [
                [
                    Np[k][i] * Np[k][j] * self.detJ[k] * self.c * self.ro for i in range(4)
                ] for j in range(4)
            ] for k in range(4)
        ]
        self.C = [
            [
                tmp[0][j][i] + tmp[1][j][i] + tmp[2][j][i] + tmp[3][j][i] for i in range(4)
            ] for j in range(4)
        ]

    def generate_matrix_bc_H(self):
        points = [
            (-1 / sqrt(3), -1),
            (1 / sqrt(3), -1),
            (1, -1 / sqrt(3)),
            (1, 1 / sqrt(3)),
            (1 / sqrt(3), 1),
            (-1 / sqrt(3), 1),
            (-1, 1 / sqrt(3)),
            (-1, -1 / sqrt(3)),
        ]
        n = N()
        bcH = [[0] * 4 for i in range(4)]
        for z in range(4):
            index0, index1 = z, z+1
            if index1 >= len(self.element.nodes):
                index1 = 0
            self.length[z] = sqrt(pow(self.element.nodes[index0].coord[0] - self.element.nodes[index1].coord[0], 2) + pow(self.element.nodes[index0].coord[1] - self.element.nodes[index1].coord[1], 2))
            if self.element.nodes[index0].bc and self.element.nodes[index1].bc:
                pN = [
                    [n[i](*points[z * 2]) for i in range(4)],
                    [n[i](*points[z * 2 + 1]) for i in range(4)]
                ]
                pc0 = [
                    [
                        pN[0][j] * pN[0][i] * self.alfa for i in range(4)
                    ] for j in range(4)
                ]
                pc1 = [
                    [
                        pN[1][j] * pN[1][i] * self.alfa for i in range(4)
                    ] for j in range(4)
                ]
                sum = [
                    [
                        (x + y) * self.length[z]/2 for x, y in zip(list1, list2)
                    ] for list1, list2 in zip(pc0, pc1)
                ]
                bcH = [
                    [
                        x + y for x, y in zip(list1, list2)
                    ] for list1, list2 in zip(bcH, sum)
                ]
        self.H = [
            [
                a + b for a, b in zip(list1, list2)
            ] for list1, list2 in zip(self.H, bcH)
        ]

    def generate_vector_P(self):
        points = [
            (-1 / sqrt(3), -1),
            (1 / sqrt(3), -1),
            (1, -1 / sqrt(3)),
            (1, 1 / sqrt(3)),
            (1 / sqrt(3), 1),
            (-1 / sqrt(3), 1),
            (-1, 1 / sqrt(3)),
            (-1, -1 / sqrt(3)),
        ]
        n = N()
        self.P = [0] * 4

        for z in range(4):
            index0, index1 = z, z+1
            if index1 >= len(self.element.nodes):
                index1 = 0
            if self.element.nodes[index0].bc and self.element.nodes[index1].bc:
                point = [points[index0 * 2], points[index0 * 2 + 1]]
                for p in point:
                    for i in range(4):
                        self.P[i] += n[i](*p) * self.alfa * self.tot * self.length[i] / 2

    def show(self):
        self.element.show()
        print(self.H)
        print(self.C)
        print(self.P)