from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

def compute_total_chemical(model):
    agent_chems = [agent.chem for agent in model.schedule.agents if agent.chem]
    return sum(agent_chems)

class ChemAgent(Agent):
    '''A ubiquitous agent representing chemical concentration'''
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.chem = 1

    def evaporate(self):
        self.chem -= 0.1

    def step(self):
        if self.chem > 0:
            self.chem -= 0.05

class SlimeAgent(Agent):
    '''An agent that excretes chemical, senses, and moves towards higher chemical
    concentration.'''
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.chem = False # including this so the model knows that this is
        # not a chem agent
        self.is_slime = True # bool denoting that this is a slime

    def secrete(self):
        pass




class SlimeModel(Model):
    '''A model with some number of slime and ubiquitous chemical'''
    def __init__(self, N, width, height):
        self.num_agents = N # number of slime agents to add
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        # Create agents
        for i in range(width*height): # for every cell in the grid
            a = ChemAgent(i, self) # generate a chem agent
            self.schedule.add(a) # add to the schedule

            # Add agent to every grid cell
            for row in range(height): # for every row
                for col in range(width): # for every column
                    self.grid.place_agent(a, (row, col)) # place a chem agent

        # Initialize datacollector
        self.datacollector = DataCollector(
        model_reporters={"Total_Chem": compute_total_chemical}, # compute defined above
        agent_reporters={"Chem": "chem"}
        )

    def step(self):
        '''advance the model by one step'''
        self.datacollector.collect(self)
        self.schedule.step()
