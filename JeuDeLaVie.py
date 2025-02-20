from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
import random


class Cell(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = random.randint(0,1)
        
    def updrade(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        sum = 0
        for neighbor in neighbors:
            sum += neighbor.state
             
        if self.state == 1 and not(sum == 2 or sum == 3):
            self.state = 0
        elif self.state == 0 and sum == 3:
            self.state = 1
    
    def step(self):
        
        print(f"Agent {self.unique_id} est à la position {self.pos} et est dans l'état {self.state} ")
        
class ConwayModel(Model):
    def __init__(self, width, height):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)

        # Créer des agents fourmis
        for i in range(width):
            for j in range(height):
                cell = Cell((i*10+j), self)
                self.grid.place_agent(cell, (i,j))
                self.schedule.add(cell)

    def step(self):
        self.schedule.step()
        
        
if __name__ == '__main__':
    # Initialiser le modèle avec une grille de 10x10 et 5 fourmis
    conway_model = ConwayModel(5, 5)
    

    for i in range(10):
        print ("-------------- STEP {i} ---------------")
        conway_model.step()

