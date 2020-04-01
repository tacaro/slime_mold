# Running the model - script
from MoneyModel import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mesa.batchrunner import BatchRunner

'''Running the batchrunner'''
fixed_params = {
    "width": 10,
    "height": 10
}

variable_params = {"N": range(10, 500, 10)}

# The variables parameters will be invoke along with the fixed parameters allowing for either or both to be honored.
batch_run = BatchRunner(
    MoneyModel,
    variable_params,
    fixed_params,
    iterations=5,
    max_steps=100,
    model_reporters={"Gini": compute_gini}
)

batch_run.run_all()

run_data = batch_run.get_model_vars_dataframe()
run_data.head()
plt.scatter(run_data.N, run_data.Gini)

'''create the model'''
model = MoneyModel(50,10,10)
for i in range(100):
    model.step()
'''^^^This is the essential step^^^'''

gini = model.datacollector.get_model_vars_dataframe()
gini.plot()
plt.show()

agent_wealth = model.datacollector.get_agent_vars_dataframe()
agent_wealth.head()

end_wealth = agent_wealth.xs(99, level="Step")["Wealth"]
end_wealth.hist(bins=range(agent_wealth.Wealth.max()+1))
plt.show()

one_agent_wealth = agent_wealth.xs(14, level="AgentID")
one_agent_wealth.Wealth.plot()
plt.show()

'''Create a numpy array of the same size as the grid, filled with zeros.
We then use the grid object's coord_iter() feature which lets us loop
over every cell in the grid, giving us each cell's coordinates and contents
in turn'''
'''
agent_counts = np.zeros((model.grid.width, model.grid.height))
for cell in model.grid.coord_iter():
    cell_content, x, y = cell
    agent_count = len(cell_content)
    agent_counts[x][y] = agent_count
plt.imshow(agent_counts, interpolation='nearest')
plt.colorbar()

# If running from a text editor or IDE, remember you'll need the following:
plt.show()
'''
