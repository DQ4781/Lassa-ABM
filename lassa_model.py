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
import math


class superAgent(Agent):

    def __init__(self, unique_id, model, init_infection, transmissibility, level_of_movement, 
    contagious_period, rodenticide, rat_trap, safe_food_storage, hygienic_housing, is_human):
        # Takes cares of the background stuff needed to create a Mesa 'Agent'
        super().__init__(unique_id, model)

        # Theses parameters define the attributes that make up a human agent
        if is_human:
            self.hum_init_infection         = init_infection
            self.h2h_transmissibility       = transmissibility
            self.level_of_hum_movement      = level_of_movement
            self.contagious_period_hum      = contagious_period
            self.rodenticide                = rodenticide
            self.rat_trap                   = rat_trap
            self.hygienic_housing           = hygienic_housing
            self.safe_food_storage          = safe_food_storage
            self.is_human                   = True
            self.adoption_group             = False
            self.kill_chance                = 0
            self.secondary_transmission_h2h = 0
        # Theses parameters define the attributes that make up a rat agent
        else:
            self.rat_init_infection         = init_infection
            self.r2h_transmissibility       = transmissibility
            self.contagious_period_rat      = contagious_period
            self.level_of_rat_movement      = level_of_movement
            self.is_human                   = False
            self.secondary_transmission_r2h = 0
        
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
                            self.secondary_transmission_h2h += 1
                    # R2H Transmission
                    elif not self.is_human:
                        if random.uniform(0, 100) < self.r2h_transmissibility:
                            resident.infected = True
                            self.secondary_transmission_r2h += 1
                # R2R Transmission
                elif not resident.is_human and not resident.infected:
                    if random.uniform(0, 100) < self.r2r_transmissibility:
                        resident.infected = True
                    

class lassaModel(Model):

    def __init__(self, N_humans, N_rats, adoption_rate,width, height, hum_init_infection, rat_init_infection, hum_transmissibility, rat_transmissibility, hum_level_of_movement, rat_level_of_movement, 
    contagious_period_hum, contagious_period_rat, rodenticide, rat_trap, safe_food_storage, hygienic_housing):
        self.running            = True
        self.num_humans         = N_humans
        self.num_rats           = N_rats
        self.grid               = MultiGrid(width, height, True)
        self.schedule           = RandomActivation(self)
        self.adoption_rate      = adoption_rate
        self.rodenticide        = rodenticide
        self.rat_trap           = rat_trap
        self.safe_food_storage  = safe_food_storage
        self.hygienic_housing   = hygienic_housing

        # Creates human agents
        for i in range(self.num_humans):
            human = superAgent(2*i, self, hum_init_infection, hum_transmissibility, hum_level_of_movement, contagious_period_hum, 
            rodenticide, rat_trap, safe_food_storage, hygienic_housing, is_human=True)
            self.schedule.add(human)

            try:
                start_cell = self.grid.find_empty()
                self.grid.place_agent(human, start_cell)
            except:
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)
                self.grid.place_agent(human, (x,y))

            # Once we added human agents to the scheduler, check if any of scenarios are turned on in order to randomly assign human agents to the adoption group 
            if rodenticide or rat_trap or safe_food_storage or hygienic_housing:
                determine_adoption_population(self)
                update_kill_chance(self)


        # Creates rat agents
        for i in range(self.num_rats):
            rat = superAgent((2*i)+1, self, rat_init_infection, rat_transmissibility, rat_level_of_movement, contagious_period_rat, is_human=False, rodenticide=0, rat_trap=0, hygienic_housing=0, safe_food_storage=0)
            self.schedule.add(rat)

            try:
                start_cell = self.grid.find_empty()
                self.grid.place_agent(rat, start_cell)
            except:
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)
                self.grid.place_agent(rat, (x,y))

            # If any of the scenarios are turned on, they we must update the rates accordingly
            if rodenticide or rat_trap or safe_food_storage or hygienic_housing:
                update_r2h_trans(self)


        self.datacollector = DataCollector(
            model_reporters={"H2H Reproduction Number":calculate_human_reproduction_number,
                             "R2H Reproduction Number":calculate_rat_reproduction_number, 
                             "Daily H2H Infections":calculate_human_secondary_infections,
                             "Daily R2H Infections":calculate_rat_secondary_infections
                            },
            agent_reporters={}
        )


    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        resetInfections(self)

# Graph Functions

def calculate_human_secondary_infections(model):

    human_secondary_infections = 0
    agent_list = model.schedule.agents

    for x in agent_list:
        if x.is_human:
            human_secondary_infections += x.secondary_transmission_h2h

    return human_secondary_infections


def calculate_rat_secondary_infections(model):

    rat_secondary_infections = 0

    agent_list = model.schedule.agents

    for x in agent_list:
        if not x.is_human:
            rat_secondary_infections += x.secondary_transmission_r2h

    return rat_secondary_infections


def calculate_human_reproduction_number(model):
    h2h_trans_rate          = 20
    h2h_trans_avg           = calculate_avg_secondary_infection(model, "Human")
    hum_contagious_period   = 12

    h2h_r0 = h2h_trans_rate * h2h_trans_avg * hum_contagious_period

    return h2h_r0


def calculate_rat_reproduction_number(model):
    r2h_trans_rate          = determine_r2h_trans_rate(model)
    r2h_trans_avg           = calculate_avg_secondary_infection(model, "Rat")
    rat_contagious_period   = 21

    r2h_r0 = r2h_trans_rate * r2h_trans_avg * rat_contagious_period

    return r2h_r0 


# Helper Functions

def resetInfections(model):

    agent_list = model.schedule.agents

    for x in agent_list:
        if x.is_human:
            x.secondary_transmission_h2h = 0
        else:
            x.secondary_transmission_r2h = 0


def calculate_avg_secondary_infection(model, agentType):
    num_humans       = 0
    num_rats         = 0
    total_agent_list = model.schedule.agents

    # Counts how many total human/rat agents there are
    for x in total_agent_list:
        if x.is_human:
            num_humans += 1
        else:
            num_rats += 1

    if agentType == "Human":
        avg = calculate_human_secondary_infections(model) / num_humans
    elif agentType == "Rat":
        avg = calculate_rat_secondary_infections(model) / num_rats

    return avg


def determine_r2h_trans_rate(model):

    for agent in model.schedule.agents:
        if not agent.is_human:
            rate = agent.r2h_transmissibility

    return rate


def determine_adoption_population(model):

    adoption_rate_percent       = model.adoption_rate/100
    adoption_size               = math.floor(adoption_rate_percent * model.num_humans)

    adoption_group_list = random.sample(model.schedule.agents, k=adoption_size)

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


def update_r2h_trans(model):

    r2h_rate = 60

    if model.safe_food_storage and model.hygienic_housing:
        r2h_rate = 2
    elif model.hygienic_housing:
        r2h_rate = 12
    elif model.safe_food_storage:
        r2h_rate = 33

    for i in model.schedule.agents:
        if not i.is_human:
            i.r2h_transmissibility = r2h_rate


