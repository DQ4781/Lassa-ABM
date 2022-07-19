"""
    Author      : Daniel Quezada
    PI          : Dr. Samspon Akwafuo
    File Name   : lassa_server.py
    Date        : 7/9/22
"""
from lassa_model import lassaModel
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule

def agent_portrayal(agent):
    # Susceptible human
    portrayal = {"Shape":"hum-sc.png", "Filled":"true", "Layer":1}

    # Infected human
    if agent.is_human == True and agent.infected:
        portrayal["Shape"] = "hum-if.png"
        portrayal["Layer"] = 0
    # Susceptible rat
    elif agent.is_human == False and not agent.infected:
        portrayal["Shape"] = "rat-sc.png"
        portrayal["Layer"] = 2
    # Infeceted rat
    elif agent.is_human == False and agent.infected:
        portrayal["Shape"] = "rat-if.png"
        portrayal["Layer"] = 3

    return portrayal



# Setups how the grid is going to be displayed on the webpage
grid = CanvasGrid(agent_portrayal, 20, 20, 700, 700)





# Creates our charts
total_infected_graph = ChartModule(
    [{"Label":"Total Humans Infected", "Color":"Red"}],
    data_collector_name='datacollector'
    )

total_secondary_infections_graph = ChartModule(
    [{"Label":"Daily H2H Infections", "Color":"Green"},
     {"Label":"Daily R2H Infections", "Color":"Violet"}], 
    data_collector_name='datacollector'
)




# Set up user sliders
num_human_slider = UserSettableParameter(
        'slider', "Number of Human Agents", 20, 2, 200, 1)

num_rat_slider = UserSettableParameter(
        'slider', "Number of Rat Agents", 5, 2, 200, 1)

hum_init_infection_slider = UserSettableParameter(
    'slider', "Probability of Human Initial Infection(%)", 30, 1, 100, 1)

rat_init_infection_slider = UserSettableParameter(
    'slider', "Probability of Rat Initial Infection(%)", 50, 1, 100, 1)

hum_transmissibility_slider = UserSettableParameter(
    'slider', "Transmissibilty between H2H", 20, 1, 100, 1)

rat_transmissibility_slider = UserSettableParameter(
    'slider', "Transmissibilty between R2H", 40, 1, 100, 1)

hum_level_of_movement_slider = UserSettableParameter(
    'slider', "Level of movement for humans", 45, 1, 100, 1)

rat_level_of_movement_slider = UserSettableParameter(
    'slider', "Level of movement for rats", 65, 1, 100, 1)

hum_contagious_period_slider = UserSettableParameter(
    'slider', "Contagious period for humans(days)", 12, 2, 21, 1)

rat_contagious_period_slider = UserSettableParameter(
    'slider', "Contagious period for rats(days)", 21, 2, 84, 1)

hum_rodenticide_slider = UserSettableParameter(
    'slider', "Humans that use rodenticide(%)", 10, 0, 100, 1)

rat_trap_slider = UserSettableParameter(
    'slider', "Humans that use rat traps(%)", 10, 0, 100, 1)

food_storage_slider = UserSettableParameter(
    'slider', "Humans that use practice safe food storage(%)", 10, 0, 100, 1)

hygienic_housing_slider = UserSettableParameter(
    'slider', "Humans that have hygienic housing(%)", 10, 0, 100, 1)




server = ModularServer(lassaModel, [grid, total_infected_graph, total_secondary_infections_graph], "Intervention Strategies for the Control of Periodic Lassa Fever Outbreaks", 
    {   
        "N_humans": num_human_slider, 
        "N_rats": num_rat_slider, 
        "width": 20,
        "height":20,
        "hum_init_infection": hum_init_infection_slider,
        "rat_init_infection": rat_init_infection_slider,
        "hum_transmissibility": hum_transmissibility_slider,
        "rat_transmissibility": rat_transmissibility_slider,
        "hum_level_of_movement": hum_level_of_movement_slider,
        "rat_level_of_movement": rat_level_of_movement_slider,
        "contagious_period_hum": hum_contagious_period_slider,
        "contagious_period_rat": rat_contagious_period_slider,
        "rodenticide": hum_rodenticide_slider,
        "rat_trap": rat_trap_slider,
        "safe_food_storage": food_storage_slider,
        "hygienic_housing": hygienic_housing_slider    
    }
)