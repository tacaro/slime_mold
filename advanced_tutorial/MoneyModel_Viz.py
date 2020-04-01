from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.batchrunner import BatchRunner
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

# If MoneyModel.py is where your code is:
from MoneyModel import MoneyModel

'''CanvasGrid works by looping over each cell in a grid and rendering
every agent it finds. A render is a dictionary that tells JavaScript
how to draw it. The only thing required is a function taking an
agent as an argument, and returns a portrayal object.

For example: draw each agent as a red, filled circle which fills
half of a cell'''

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if agent.wealth > 0:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal

'''In addition to the portrayal method, we can instantiate a canvas
grid with its width/height in cells and in pixels. For example,
let's make a 10x10 grid, drawn in 500x500 pixels:'''

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

'''To create and launch the server, we use:
Model class we're running and visualizing, 'MoneyModel'
List of module objects to include: here, just 'grid'
Title of the model, "Money Model"
Inputs or arguments for the model itself: 100 agents, height and width"

Once we create the server, we set the port, and use the launch() function
'''

chart = ChartModule([{"Label": "Gini",
                      "Color": "Black"}],
                    data_collector_name='datacollector')
# the label must match the model-level variable collected by DataCollector
#data_collector_name must match the data collector object name


server = ModularServer(MoneyModel,
                       [grid, chart],
                       "Money Model",
                       {"N":100, "width":10, "height":10})
server.port = 8521 # The default
server.launch()
