from tkinter import *

import spectra
import time
import threading

from structures.element import *
from structures.grid import *


def time_step(k, c, ro, x, y):
    asr = k / (c * ro)
    return pow(x / y, 2) / (0.5 * asr * 1000)


class Application:
    def __init__(self, master=None):
        data = read_json_from_file("data.json")

        self.master = master
        master.title("MES by Damian Hałatek")
        self.width = 800
        self.height = 800

        self.t = data["initial_temperature"]
        self.Y = data["Y"]
        self.nY = data["nY"]

        self.tot = data["ambient_temperature"]

        self.time = data["time"]
        self.step = data["step"]    # time_step(25, 840, 2500, 0.03, 0.1)

        self.color_scale = spectra.scale(['blue', 'red'])

        self.layers_input = data["layers"]

        self.canvas = Canvas(master, width=self.width, height=self.height, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=10, rowspan=20)

        self.start_button = Button(master, text="START", command=self.initialize)
        self.start_button.grid(row=0, column=11)

        self.grid = self.initialize_grid()
        self.draw()

    def initialize(self):
        t = threading.Thread(target=self.calculate)
        t.start()

    def calculate(self):
        for i in range(int(self.time / self.step)):
            self.grid.calculate()
            self.draw()

    def initialize_grid(self):
        previous = 0
        nodes = []
        elements = []

        dy = self.Y / (self.nY - 1)
        id = 0

        for i in range(self.nY):
            nodes.append(Node(id, (0, dy * i), self.t))
            id += 1

        for layer in self.layers_input:
            dx = layer["X"] / layer["nX"]
            for i in range(1, layer["nX"] + 1):
                for j in range(self.nY):
                    nodes.append(Node(id, (dx * i + previous, dy * j), self.t))
                    id += 1
            previous += layer["X"]

        previous = 0
        for layer in self.layers_input:
            nL = layer["nX"]
            for i in range(previous, previous + nL):
                for j in range(0, self.nY - 1):
                    tmp = [nodes[i * self.nY + j], nodes[(i + 1) * self.nY + j], nodes[(i + 1) * self.nY + j + 1], nodes[i * self.nY + j + 1]]
                    elements.append(Element(tmp, layer["alfa"], layer["specific_heat"], layer["conductivity"], layer["density"]))

            previous += nL

        nodes_len = len(nodes)
        elements_len = len(elements)

        for j in range(0, self.nY - 1):     # set bc and tot
            elements[j].tot = self.tot
            elements[elements_len - j - 1].tot = self.t
            nodes[j].bc = True
            nodes[nodes_len - j - 1].bc = True

        return Grid(nodes, elements, self.step)

    def draw(self):
        w = self.canvas
        w.delete("GRID")
        size = (self.width - 100) / self.Y
        offset_x, offset_y = 50, 50

        for element in self.grid.elements:
            coords = []
            avg_temp = 0
            for node in element.nodes:
                coords.append(node.coord[0] * size + offset_x)
                coords.append(node.coord[1] * size + offset_y)
                avg_temp += node.t
            avg_temp /= 4
            color = self.color_scale(avg_temp / self.tot).hexcode
            w.create_polygon(coords, fill=color, tags="GRID")

        for node in self.grid.nodes:
            x1, y1 = node.coord[0] * size - 5 + offset_x, node.coord[1] * size - 5 + offset_y
            x2, y2 = node.coord[0] * size + 5 + offset_x, node.coord[1] * size + 5 + offset_y
            color = self.color_scale(node.t / self.tot).hexcode
            w.create_oval(x1, y1, x2, y2, fill=color, tags="GRID")



if __name__ == "__main__":
    root = Tk()
    app = Application(master=root)
    root.mainloop()
