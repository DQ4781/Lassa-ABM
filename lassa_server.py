"""
    Author      : Daniel Quezada
    PI          : Dr. Sampson Akwafuo
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
grid = CanvasGrid(agent_portrayal, 30, 30, 800, 800)





# Creates our SIR graph 
sir_graph = ChartModule(
    [{"Label":"Susceptible Humans", "Color":"SlateBlue"},
     {"Label":"Infected Humans", "Color":"Salmon"},
     {"Label":"Removed Humans", "Color":"LimeGreen"}],
    data_collector_name='datacollector'
    )





# Set up user sliders
num_human_slider = UserSettableParameter(
        'slider', "Number of Human Agents", 140, 100, 300, 1)

num_rat_slider = UserSettableParameter(
        'slider', "Number of Rat Agents", 240, 100, 400, 1)

adoption_rate_slider = UserSettableParameter(
    'slider', "Human Agents that Adopt Intervention Strategies(%)", 0, 0, 100, 1)

hum_case_fatality_slider = UserSettableParameter(
    'slider', "Probability that infected human dies every step", 1, 1, 10, 1)

hum_init_infection_slider = UserSettableParameter(
    'slider', "Probability of Human Initial Infection(%)", 5, 1, 100, 1)

rat_init_infection_slider = UserSettableParameter(
    'slider', "Probability of Rat Initial Infection(%)", 30, 1, 100, 1)

hum_transmissibility_slider = UserSettableParameter(
    'slider', "Transmissibilty between H2H", 20, 1, 100, 1)

rat_transmissibility_slider = UserSettableParameter(
    'slider', "Transmissibilty between R2H", 35, 1, 100, 1)

hum_level_of_movement_slider = UserSettableParameter(
    'slider', "Level of movement for humans", 25, 1, 100, 1)

rat_level_of_movement_slider = UserSettableParameter(
    'slider', "Level of movement for rats", 65, 1, 100, 1)

hum_contagious_period_slider = UserSettableParameter(
    'slider', "Contagious period for humans(days)", 21, 7, 30, 1)

rat_contagious_period_slider = UserSettableParameter(
    'slider', "Contagious period for rats(days)", 80, 21, 90, 1)


# Set up user checkboxes
hum_rodenticide_checkbox = UserSettableParameter(
    'checkbox', "Humans that use rodenticide", value=False)

rat_trap_checkbox = UserSettableParameter(
    'checkbox', "Humans that use rat traps", value=False)


server = ModularServer(lassaModel, [grid, sir_graph], "Intervention Strategies for the Control of Periodic Lassa Fever Outbreaks", 
    {   
        "N_humans": num_human_slider, 
        "N_rats": num_rat_slider,
        "adoption_rate":adoption_rate_slider,
        "hum_case_fatality":hum_case_fatality_slider,
        "width": 30,
        "height":30,
        "hum_init_infection": hum_init_infection_slider,
        "rat_init_infection": rat_init_infection_slider,
        "hum_transmissibility": hum_transmissibility_slider,
        "rat_transmissibility": rat_transmissibility_slider,
        "hum_level_of_movement": hum_level_of_movement_slider,
        "rat_level_of_movement": rat_level_of_movement_slider,
        "contagious_period_hum": hum_contagious_period_slider,
        "contagious_period_rat": rat_contagious_period_slider,
        "rodenticide": hum_rodenticide_checkbox,
        "rat_trap": rat_trap_checkbox    
    }
)