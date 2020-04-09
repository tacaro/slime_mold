from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


'''Here we define functions applied at the model-wide scale'''
def compute_total_chemical(model):
    agent_chems = [agent.chem for agent in model.schedule.agents if isinstance(agent, ChemAgent)]
    return sum(agent_chems)


'''Here we define the two kinds of agents the model accepts: slime and chem'''
class ChemAgent(Agent):
    '''
    An agent representing chemical concentration. This will be spawned in
    every gridspace and hold a float value representing chemical concentration.
    '''
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.chem = 0

    def step(self):
        '''
        The agent shares chemical with surrounding cells through diffusion.
        Chemical is also lost due to evaporation.
        '''
        if self.chem > 0:
            for neighbor in self.model.grid.neighbor_iter(self.pos):
                if isinstance(neighbor, ChemAgent):
                    neighbor.chem += (self.chem * 0.2) # adds 20% of value to neighbor
                    self.chem -= (self.chem * 0.2) # subtracts 20% of value from self
            self.chem -= 0.001 # loss due to evaporation

class SlimeAgent(Agent):
    '''
    An agent that excretes chemical, senses, and moves towards higher chemical
    concentration. This agent represents a single slime mold cell.
    '''
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.chem = 0

    def secrete(self):
        '''The agent adds chemical to its surrounding cells'''
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if isinstance(neighbor, ChemAgent):
                neighbor.chem += 0.5 # add 0.02 chemical to neighboring cells

    def move(self):
        '''The agent sniffs the surrounding cells for the highest concentration
        of chemical - it them moves to that cell.'''
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=False,
            radius=1
        )

        curIndex = 0
        idx =0
        temp = 0
        while(curIndex < len(neighbors)):
            if(temp < neighbors[curIndex].chem):
                temp = neighbors[curIndex].chem # save the objattr
                idx = curIndex # save the idx
            curIndex +=1 # increment idx
        optimal = neighbors[idx] # assign obj w/ said index

        new_position = optimal.pos # identify the position of the optimal obj
        self.model.grid.move_agent(self, new_position)



    def step(self):
        self.move()
        self.secrete()



'''Below we define the model parameters'''

class SlimeModel(Model):
    '''
    A model with some number of slime and ubiquitous chemical
    Args:
        pop: number of slime cells to add to the model
        width: grid width
        height: grid height
    '''
    def __init__(self, pop, width, height):
        self.N = pop # number of slime agents to spawn
        self.grid = MultiGrid(width, height, False) # torus = False
        self.schedule = RandomActivation(self)
        self.running = True

        # Create agents

        # Add chem agent to every grid cell
        for row in range(height): # for every row
            for col in range(width): # for every column
                id = ((row*10) + col) # unique_id is row,col as 2 digit number
                a = ChemAgent(id, self) # generate a chem agent
                self.schedule.add(a) # add to the schedule
                self.grid.place_agent(a, (row, col)) # place a chem agent

        # Add slime agent randomly, population specified by N
        for i in range(self.N):
            slm = SlimeAgent(i, self)
            self.schedule.add(slm)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(slm, (x, y))

        # Initialize datacollector
        self.datacollector = DataCollector(
        model_reporters={"Total_Chem": compute_total_chemical}, # compute defined above
        agent_reporters={"Chem": "chem"}
        )

    def step(self):
        '''advance the model by one step'''
        self.datacollector.collect(self)
        self.schedule.step()
