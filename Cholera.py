# Tarvail réalisé par Salwa AZARIOUH et Alexandre MARTEL


from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random
from enum import IntEnum

class State(IntEnum):
    SUSCEPTIBLE = 0 #susceptible d'être infecté
    EXPOSED = 1
    INFECTED_LOW = 2 # Benin
    INFECTED_HARD = 3 # Grave
    RECOVERED = 4 #Ne peut être infecté

class Background(IntEnum):
    PROLETAIRE = 0
    MOYEN = 1
    BOURGEOIS = 2 
    VILLAGEOIS = 3
    
class Genre(IntEnum):
    GARCON = 0
    FILLE = 1
    HOMME = 2
    FEMME = 3


class Person(Agent):
    def __init__(self, unique_id, background, model, health_state=State.SUSCEPTIBLE, water_source=None, ):
        super().__init__(unique_id, model)
        self.health_state = health_state  # S (Susceptible), E (Exposed), I (Infected), R (Recovered)
        self.water_source = water_source  # Point d'eau où l'agent se rend
        self.genre = random.choices([Genre.GARCON, Genre.FILLE, Genre.HOMME, Genre.FEMME], [0.15,0.15,0.35,0.35])  # Assignation d'un âge aléatoire
        self.time_infected = 0  # Durée depuis laquelle l'agent est infecté
        self.background = background  #Classe sociale de l'individu
        self.time_recovered = 0 # Durée depuis laquelle l'agent est guérit
    
    def recover_or_die_hard(self):
        
        if self.random.random() < 0.05:  # 5% de chance de mourir
            self.model.grid.remove_agent(self)
            self.model.schedule.remove_agent(self)
        else: 
            self.health_state = State.RECOVERED  # Guéri
            self.time_infected = 0
            
    def recover_or_die_low(self):
        
        self.health_state = State.RECOVERED  # Guéri
        self.time_infected = 0

    def recovered(self):
        if self.time_recovered > 240:
            self.health_state = State.SUSCEPTIBLE
            self.time_recovered = 0
            
    def drink_water(self):
        if self.water_source and self.water_source.contaminated:
            if self.health_state == State.SUSCEPTIBLE and self.random.random() < 0.3:  # 30% de chance d'être exposed
                self.health_state = State.EXPOSED  # Passe de Susceptible à Exposed
        elif self.water_source and not(self.water_source.contaminated):
            if self.health_state == State.EXPOSED:
                self.water_source.contaminated = True
                
    def contact(self):
        #je vérifie s'il y a d'autres agents avec moi dans la même case
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        
        #si je ne suis pas tout seul et je suis infecté
        if len(cellmates)>1 and (self.health_state == State.INFECTED_LOW or self.health_state == State.INFECTED_HARD):
            
            # self.model.ptrans attribut à définir au niveau du modèle
            for other in cellmates:
                if other.health_state == State.SUSCEPTIBLE and self.random.random() < self.model.ptrans :
                    other.health_state = State.EXPOSED
    
    def move(self):
        #récupérer la liste des positions autour de la case là ou la cellule se trouve
        possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True, include_center=True)
        
        new_position = self.random.choice(possible_steps)
        
        self.model.grid.move_agent(self, new_position) #l'attribut self.pos va changer automatiquement
        
    def status(self):
        if self.health_state == State.EXPOSED:
            self.time_infected += 1
            if (self.time_infected >= 2 and random.randint(0,2) == 2) or self.time_infected == 5:  
                
                self.health_state = random.choices([State.INFECTED_HARD, State.INFECTED_LOW], [0.1, 0.9])
                
        elif self.health_state == State.INFECTED_HARD and self.time_infected >= 5:
            self.recover_or_die_hard()
        
        elif self.health_state == State.INFECTED_LOW and self.time_infected >= 10:
            self.recover_or_die_low()
            
        elif self.health_state == State.RECOVERED:
            self.time_recovered += 1
            self.recovered()
        
    def step(self):
        
        self.move()
        self.contact()
        self.status()
    
            
class CholeraModel(Model):
    def __init__(self, width, height, population, ptrans):
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        # Initialiser les agents humains
        for number_type in range(population):
            
            if number_type == 0:
                background = State.PROLETAIRE
            if number_type == 1:
                background = State.VILLAGOIS
            if number_type == 2:
                background = State.MOYEN
            if number_type == 3:
                background = State.BOURGEOIS
                
            for i in range(population[number_type]):
                person = Person(number_type*100 + i, self, background)
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                self.grid.place_agent(person, (x, y))
                self.schedule.add(person)

        # Initialiser des sources d'eau et infrastructures
        for i in range(10):  # On rajoute 10 points d'eau
            water_source = WaterSource(self.next_id(), self, contaminated=False)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(water_source, (x, y))
            
    def step(self):
        for agent in self.schedule.agent_buffer(shuffled=True):
            if isinstance(agent, Person):
                if agent.health_state == "I":  # Si l'agent est infecté
                    agent.drink_water()  # Boit de l'eau, potentiellement contaminée
            self.schedule.step()  # Avance la simulation d'un pas

class WaterSource(Agent):
    def __init__(self, unique_id, model, contaminated=False):
        super().__init__(unique_id, model)
        self.contaminated = contaminated

    def step(self):
        pass
        
        
if __name__ == '__main__':
   
    CholeraModel = CholeraModel(30, 30, [30,15,20,5], 0.3)
    

    #for i in range(10):
    #    print ("-------------- STEP "+i+ " ---------------")
    #    CholeraModel.step()
    
steps=400
pop=400

output_notebook()

model = InfectionModel(pop, 20, 20, ptrans=0.25, death_rate=0.01)
for i in range(steps):
    model.step()
    
    p1=plot_states_bokeh(model,title='step=%s' %i)
    p2=plot_cells_bokeh(model) 
    
    show(p1)
    show(p2)
