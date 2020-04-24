from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import * # our model module
import argparse

# We need to provide that takes an agent, returns a portrayal object
'''Universal Parameters'''
width = 20 # width of grid
height = 20 # height of grid
slime_population = 20 # how many slime cells to add
arena_size = 750 # grid cell width in pixels

def agent_portrayal(agent):
    if isinstance(agent, ChemAgent):
        if agent.chem > 0 and agent.chem < 2:
            portrayal = {"Shape": "circle",
                         "Color": "blue",
                         "Filled": "true",
                         "Layer": 0,
                         "r": agent.chem}
        elif agent.chem >= 2: # max the radius at 2 so we don't overload the image
            portrayal = {"Shape": "circle",
                         "Color": "blue",
                         "Filled": "true",
                         "Layer": 0,
                         "r": 2}
        else:
            portrayal = {"Shape": "rect",
                         "Color": "white",
                         "Filled": "true",
                         "Layer": 0,
                         "w": 1,
                         "h": 1}
    if isinstance(agent, SlimeAgent):
        portrayal = {"Shape": "circle",
                     "Color": "red",
                     "Filled": "true",
                     "Layer": 1,
                     "r": 0.33}
    return portrayal

# Instantiate canvas grid with width and height in cells/pixels
grid = CanvasGrid(agent_portrayal, width, height, arena_size, arena_size)

# Create a chart for the total amount of chemical
chart1 = ChartModule([{"Label": "Total_Chem",
                      "Color": "Black"}],
                      data_collector_name='datacollector')

chart2 = ChartModule([{"Label": "Average_Distance",
                      "Color": "Red"}],
                      data_collector_name='datacollector')

# Create and launch the server
server = ModularServer(SlimeModel, # the model to feed in
                       [grid, chart1, chart2], # the list of objects to include in the viz
                       "Slime Model", # title
                       {"pop":slime_population, "width":width, "height":height}) # arguments for the model

server.port = 8251 # the default port
server.launch()
