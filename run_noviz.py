from model import *
import matplotlib.pyplot as plt
import numpy as np

model = SlimeModel(50, 20, 20)
for i in range(100):
    model.step()

end_chem = [a.chem for a in model.schedule.agents if a.chem]
plt.hist(end_chem)
plt.show()

chemXtime = model.datacollector.get_model_vars_dataframe()
chemXtime.plot()
plt.show()

agent_counts = np.zeros((model.grid.width, model.grid.height))
for cell in model.grid.coord_iter():
    cell_content, x, y = cell
    agent_count = len(cell_content)
    agent_counts[x][y] = agent_count
plt.imshow(agent_counts, interpolation='nearest')
plt.colorbar()
plt.show()
