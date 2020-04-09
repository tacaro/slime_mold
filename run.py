from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import * # our model module

# We need to provide that takes an agent, returns a portrayal object

def agent_portrayal(agent):
    if agent.chem:
        portrayal = {"Shape": "circle",
                     "Color": "red",
                     "Filled": "true",
                     "Layer": 0,
                     "r": agent.chem}

    return portrayal

# Instantiate canvas grid with width and height in cells/pixels
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

# Create a chart for the total amount of chemical
chart = ChartModule([{"Label": "Total_Chem",
                      "Color": "Black"}],
                      data_collector_name='datacollector')

# Create and launch the server
server = ModularServer(SlimeModel, # the model to feed in
                       [grid, chart], # the list of objects to include in the viz
                       "Slime Model", # title
                       {"N":100, "width":20, "height":20}) # arguments for the model
server.port = 8251 # the default port
server.launch()
