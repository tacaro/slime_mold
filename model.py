from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
from scipy.spatial.distance import pdist
from sklearn.neighbors import DistanceMetric



'''Here we define functions applied at the model-wide scale'''


def compute_total_chemical(model):
    agent_chems = [agent.chem for agent in model.schedule.agents if isinstance(
                    agent, ChemAgent)]
    return sum(agent_chems)

def compute_distance_matrix(model):
    agent_pos = [agent.pos for agent in model.schedule.agents if isinstance(
                 agent, SlimeAgent)]
    agent_pos = [list(tup) for tup in agent_pos]
    dist_mat = pdist(agent_pos)
    return np.average(dist_mat)

def compute_average_dist(dist_mat):
    return np.average(dist_mat)





'''Here we define the two kinds of agents the model accepts: slime and chem'''


class ChemAgent(Agent):
    '''
    An agent representing chemical concentration. This will be spawned in
    every gridspace and hold a float value representing chemical concentration.
    '''
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.chem = 0.01

    def diffuse(self):
        #figure out how many neighbors you have
        n_neighbors = len(self.model.grid.get_neighbors(self.pos,
                                                      moore=True,
                                                      include_center=False))
        #amount to diffuse into each neighbor. at first, just divided total
        #self.chem by neighbors, but then each cell loses all of it's chem.
        #so, now, only 1/2 of the total val leaks out. we can tweak this.
        #but seems to work better to multiply by some scalar < 1.

        amt_per_neighbor = 0.5*(self.chem/n_neighbors)

        for neighbor in self.model.grid.get_neighbors(self.pos,
                                                      moore=True,
                                                      include_center=False):
            if isinstance(neighbor, ChemAgent):
                neighbor.chem += amt_per_neighbor
                self.chem -= amt_per_neighbor

    def evaporate(self):
        '''All chem agents lose chemical at 0.005 per step'''
        evap_rate = 0.01
        if self.chem > evap_rate: # so that self.chem stays pos
            self.chem -= evap_rate
        else:
            self.chem = 0

    def step(self):
        '''
        The agent shares chemical with surrounding cells through diffusion.
        Chemical is also lost due to evaporation.
        '''
        self.diffuse()
        self.evaporate()


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
                neighbor.chem += 0.02  # add 0.1 chemical to neighboring cells

    def move(self):
        '''The agent sniffs the surrounding cells for the highest concentration
        of chemical - it them moves to that cell.'''
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=True,
            radius=1
        )

        curIndex = 0
        idx = 0
        temp = 0
        while(curIndex < len(neighbors)):
            if(temp < neighbors[curIndex].chem):
                temp = neighbors[curIndex].chem  # save the objattr
                idx = curIndex  # save the idx
            curIndex += 1  # increment idx
        optimal = neighbors[idx]  # assign obj w/ said index

        new_position = optimal.pos  # identify the position of the optimal obj
        self.model.grid.move_agent(self, new_position)


    def step(self):
        if (self.unique_id%10 != 0):
            self.move()
            self.secrete()
        else: #either quell secretion or moving
            #self.secrete()
            self.move()

'''Above we define the agents'''
'''Below we define the model'''


class SlimeModel(Model):
    '''
    A model with some number of slime and ubiquitous chemical
    Args:
        pop: number of slime cells to add to the model
        width: grid width
        height: grid height
    '''
    def __init__(self, pop, width, height):
        '''Initialize the model'''
        self.N = pop  # number of slime agents to spawn
        self.grid = MultiGrid(width, height, True)  # torus = True
        self.schedule = RandomActivation(self)
        self.running = True  # True so that the model runs

        # Spawn agents

        # Add chem agent to every grid cell
        for coord in self.grid.coord_iter():
            coord_content, x, y = coord # pull contents, x/y pos from coord obj
            id = str(x)+'_'+str(y) # unique_id is x_y position
            a = ChemAgent(id, self) # instantiate a chem agent
            self.schedule.add(a) # add to the schedule
            self.grid.place_agent(a, (x, y)) # spawn the chem agent

        # Add slime agent randomly, population specified by N
        for i in range(self.N):
            slm = SlimeAgent(i, self)
            self.schedule.add(slm)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(slm, (x, y))

        # Initialize datacollector
        self.datacollector = DataCollector(
        model_reporters={"Total_Chem": compute_total_chemical,
                         "Average_Distance": compute_distance_matrix},
        agent_reporters={"Chem": "chem"}
        )

    def validate(self):
        '''
        This function validates that there is a functioning ChemAgent in every
        grid space.
        '''
        chemCTR = 0
        matrixsize = self.grid.height*self.grid.width
        for agent in self.schedule.agents:
            if isinstance(agent, ChemAgent):
                chemCTR += 1
        if chemCTR == (self.grid.height*self.grid.width):
            pass
        else:
            print(chemCTR)
            print("ERROR: Chem agents not filling space")
            print(matrixsize)

    def step(self):
        '''Advances the model by one step'''
        self.validate()
        self.datacollector.collect(self)
        self.schedule.step()
