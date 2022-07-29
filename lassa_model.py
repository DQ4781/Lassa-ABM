"""
    Author      : Daniel Quezada
    PI          : Dr. Sampson Akwafuo
    File Name   : lassa_model.py
    Date        : 7/9/22
"""

from mesa import Agent, Model
from mesa.time import RandomActivation 
from mesa.space import MultiGrid 
from mesa.datacollection import DataCollector


import random

class superAgent(Agent):

    def __init__(self, unique_id, model, init_infection, transmissibility, level_of_movement, 
    contagious_period, rodenticide, rat_trap, is_human):
        # Takes cares of the background stuff needed to create a Mesa 'Agent'
        super().__init__(unique_id, model)

        # So we can access model-level variables from a single agent (used by the determine_kill_chance function)
        self.modelType = model

        # Theses parameters define the attributes that make up a human agent
        if is_human:
            self.hum_init_infection         = init_infection
            self.h2h_transmissibility       = transmissibility
            self.level_of_hum_movement      = level_of_movement
            self.contagious_period_hum      = contagious_period
            self.rodenticide                = rodenticide
            self.rat_trap                   = rat_trap
            self.is_human                   = True
            self.adoption_group             = False
            self.kill_chance                = 0
        # Theses parameters define the attributes that make up a rat agent
        else:
            self.rat_init_infection         = init_infection
            self.r2h_transmissibility       = transmissibility
            self.contagious_period_rat      = contagious_period
            self.level_of_rat_movement      = level_of_movement
            self.is_human                   = False
        
        # I HAVE NO IDEA WHY THIS DOESN'T WORK UNDER THE ELSE BLOCK; TECHINCALLY ONLY BELONGS TO RAT AGENTS 
        self.r2r_transmissibility       = 40


        # Determine if an agent (rat or human) starts off infected at the beginning of the model
        if random.uniform(0, 100) < init_infection:
            self.infected = True
        else:
            self.infected = False


    def step(self):
        # Determines if an agent (human or rat) moves at the beginning of a step
        if self.is_human:
            if random.uniform(0, 100) < self.level_of_hum_movement:
                self.move()
        else:
            if random.uniform(0, 100) < self.level_of_rat_movement:
                self.move()

        # This block checks if there is an rat and human together in the same square and calculates the probability that the human is able to exterminate the rat
        if self.is_human and self.adoption_group:
            determine_kill_chance(self)

        # Once an agents moves (or stays), we should check if the agent (rat or human) is infected and is able to infect others
        
        # Infected Human Host (only H2H possible)
        if self.is_human and self.infected:
            self.infect()
            self.contagious_period_hum -= 1

            if self.contagious_period_hum <= 0:
                self.infected = False

        # Infected Rat Host (both R2H and R2R possible)
        if not self.is_human and self.infected:
            self.infect()
            self.contagious_period_rat -= 1

            if self.contagious_period_rat <= 0:
                self.infected = False
    

    def move(self):
        # Creates a list of possible cells our agent (either rat/human) can move into (not including the cell its already on)
        neighbor_cells = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        # Choose a random cell from the list 
        new_position = random.choice(neighbor_cells)
        # Move the agent
        self.model.grid.move_agent(self, new_position)
    

    def infect(self):
        # Get a list of agents in this cell
        cellmates = self.model.grid.get_cell_list_contents([self.pos])

        # Check if there are more agents in that cell
        if len(cellmates) > 1:
            for resident in cellmates:
                if resident.is_human and not resident.infected:
                    # H2H Transmission
                    if self.is_human:
                        if random.uniform(0, 100) < self.h2h_transmissibility:
                            resident.infected = True
                    # R2H Transmission
                    elif not self.is_human:
                        if random.uniform(0, 100) < self.r2h_transmissibility:
                            resident.infected = True
                # R2R Transmission
                elif not resident.is_human and not resident.infected:
                    if random.uniform(0, 100) < self.r2r_transmissibility:
                        resident.infected = True
                    

class lassaModel(Model):

    def __init__(self, N_humans, N_rats, adoption_rate,width, height, hum_init_infection, rat_init_infection, hum_transmissibility, rat_transmissibility, hum_level_of_movement, rat_level_of_movement, 
    contagious_period_hum, contagious_period_rat, rodenticide, rat_trap):
        self.running            = True
        self.num_humans         = N_humans
        self.num_rats           = N_rats
        self.grid               = MultiGrid(width, height, True)
        self.schedule           = RandomActivation(self)


        self.hum_transmissibility   = hum_transmissibility
        self.rat_transmissibility   = rat_transmissibility
        self.contagious_period_hum  = contagious_period_hum
        self.contagious_period_rat  = contagious_period_rat
        self.adoption_rate          = adoption_rate
        self.rodenticide            = rodenticide
        self.rat_trap               = rat_trap

        # Creates human agents
        for i in range(self.num_humans):
            human = superAgent(2*i, self, hum_init_infection, hum_transmissibility, hum_level_of_movement, contagious_period_hum, 
            rodenticide, rat_trap, is_human=True)
            self.schedule.add(human)

            try:
                start_cell = self.grid.find_empty()
                self.grid.place_agent(human, start_cell)
            except:
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)
                self.grid.place_agent(human, (x,y))


        # Check if any of scenarios are turned on in order to randomly assign human agents to the adoption group 
        if rodenticide or rat_trap:
            determine_adoption_population(self)
            update_kill_chance(self)

        # Creates rat agents
        for i in range(self.num_rats):
            rat = superAgent((2*i)+1, self, rat_init_infection, rat_transmissibility, rat_level_of_movement, contagious_period_rat, rodenticide, rat_trap, is_human=False)
            self.schedule.add(rat)

            try:
                start_cell = self.grid.find_empty()
                self.grid.place_agent(rat, start_cell)
            except:
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)
                self.grid.place_agent(rat, (x,y))


        self.datacollector = DataCollector(
            model_reporters={},
            agent_reporters={}
        )


    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)







# Helper Functions Related to Rodent Control

def determine_adoption_population(model):

    adoption_rate_percent       = model.adoption_rate/100
    adoption_size               = int(adoption_rate_percent * model.num_humans)
    adoption_group_list         = random.sample(model.schedule.agents, k=adoption_size)

    for i in adoption_group_list:
        i.adoption_group = True


def update_kill_chance(model):

    if model.rodenticide and model.rat_trap:
        kill_chance = random.randint(1,16) + random.randint(40,80)
    elif model.rodenticide:
        kill_chance = random.randint(40,80)
    elif model.rat_trap:
        kill_chance = random.randint(1,16)

    for i in model.schedule.agents:
        if i.adoption_group:
            i.kill_chance = kill_chance


def determine_kill_chance(self):
    # Determine which scenarios are turned on
    poison  = self.rodenticide
    traps   = self.rat_trap

    # Calculate the probability a human agent in the adoption group is going to exterminate a rat
    kill_chance = 0

    if poison and traps:
        kill_chance = random.randint(1,16) + random.randint(40,80)
    elif poison:
        kill_chance = random.randint(40,80)
    elif traps:
        kill_chance = random.randint(1,16)

    # Get a list of agents in the same square as the human agent
    cellmates = self.model.grid.get_cell_list_contents([self.pos])

    # Determine if a rat gets killed 
    if len(cellmates) > 1:
        for agent in cellmates:
            if agent.is_human == False:
                attempt_to_kill(self, agent, kill_chance)


def attempt_to_kill(self, rat, kill_chance):
    
    # Human successfuly kills rat
    if random.uniform(0, 100) < kill_chance:
        self.modelType.grid.remove_agent(rat)
        self.modelType.schedule.remove(rat)

    

