#!/usr/bin/env python
# coding: utf-8

# GGIA Consumption Module
# authors: Peter Robert Walke (original Jupyter notebook)
#          Ulrich Norbisrath (ulno)

# Variable naming convention:
# Constants, strings, and static tables are spelled all capital letters
#
# Variable endings:
# - _T or _t: table
# - _KV or _kv: key-value
# - _loc: Local representation of a former global variable


# Loading Python Libraries
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt


## constants (mainly strings and labels) and csv tables
# they are easy to spot due to capital spelling

## CSV imports
CSV_PATH = os.path.join("..", "CSVfiles", "consumption", "")

# Load the projections for income and house size
HOUSE_SIZE_PROJ_T = pd.read_csv(CSV_PATH + "House_proj_exio.csv", index_col=0)
INCOME_PROJ_T = pd.read_csv(CSV_PATH + "Income_proj_exio.csv", index_col=0)

# Load the different Y vectors.
# The user selects which one
# to use based on the urban density of the region (or the
# average one for mixed regions or if they are unsure)
Y_VECTORS = {
    'average': pd.read_csv(CSV_PATH + "Average_2020_Exio_elec_trans_en_Euro.csv", index_col=0),
    'city': pd.read_csv(CSV_PATH + "City_2020_Exio_elec_trans_en_Euro.csv", index_col=0),
    'rural': pd.read_csv(CSV_PATH + "Rural_2020_Exio_elec_trans_en_Euro.csv", index_col=0),
    'town': pd.read_csv(CSV_PATH + "Town_2020_Exio_elec_trans_en_Euro.csv", index_col=0) }

# Load the Use phase and tail pipe emissions.
USE_PHASE_T = pd.read_csv(CSV_PATH + "Energy_use_phase_Euro.csv", index_col=0)
TAIL_PIPE_T = pd.read_csv(CSV_PATH + "Tailpipe_emissions_bp.csv", index_col=0)

# Load default house sizes
HOUSE_SIZE_T = pd.read_csv(CSV_PATH + "Household_characteristics_2015.csv", index_col=0)

# Load the Emission intensities
# EMISSION_COUNTRIES_T is the standard Emissions factors
EMISSION_COUNTRIES_T = pd.read_csv(CSV_PATH + "Country_Emissions_intensities.csv", index_col=0)

# M_countries_LCA is the same as M_countries, but with the electricity sector replaced with 
# individual LCA values
# This is useful if there is local electricity production. The user can replace certain values 
# with these values if needed
EMISSION_COUNTRIES_LCA_T = pd.read_csv(
    CSV_PATH + "Country_Emissions_intensities_LCA.csv", index_col=0)
PRODUCT_COUNT = EMISSION_COUNTRIES_T.columns
EXIO_PRODUCTS_T = pd.read_csv(CSV_PATH + "Exio_products.csv")

# Load the IW sectors
# This is needed to put the emissions into different 'sectors', such as transport, 
# food, building energy use, etc
IW_SECTORS_T = pd.read_csv(CSV_PATH + "IW_sectors_reduced.csv", index_col=0)
IW_SECTORS_NP_T = IW_SECTORS_T.to_numpy()
IW_SECTORS_NP_TR_T = np.transpose(IW_SECTORS_NP_T)

# Load the adjustable amounts.
# This says how much electricity is spent on heating. There are some other things here but
# decided not to include.
ADJUSTABLE_AMOUNTS_T = pd.read_csv(CSV_PATH + "Adjustable_energy_amounts.csv", index_col=0)

# Electricity prices database might need updating still - TODO: we could think about that later
# Load the electricity prices. This is so we know in monetary terms how much is being spent on 
# electricity. The tool
# at the moment has the electricity used by households in kWh. However, maybe this should now be 
# changed?
ELECTRICITY_PRICES_T = pd.read_csv(CSV_PATH + "electricity_prices_2019.csv", index_col=0)

# Load the fuel prices at basic price
# We need this because of electric vehicles. The electricity and fuels need to be in the same units.
FUEL_PRICES_T = pd.read_csv(CSV_PATH + "Fuel_prices_BP_attempt.csv", index_col=0)

# Load the Income scaler. This describes how much each household spends depending on their income.
INCOME_SCALING_T = pd.read_csv(CSV_PATH + "mean_expenditure_by_quint.csv", index_col=0)

# Types of electricity
# No electricity goes in ELECTRICITY_NEC. This is used for local electricity production
ELECTRICITY_NEC = 'Electricity nec'
ELECTRICITY_TYPES = [
    'Electricity by coal',
    'Electricity by gas',
    'Electricity by nuclear',
    'Electricity by hydro',
    'Electricity by wind',
    'Electricity by petroleum and other oil derivatives',
    'Electricity by biomass and waste',
    'Electricity by solar photovoltaic',
    'Electricity by solar thermal',
    'Electricity by tide, wave, ocean',
    'Electricity by Geothermal',
    ELECTRICITY_NEC]


# Supply of household heating
LIQUID_TYPES = [
    'Natural Gas Liquids',
    'Kerosene',
    'Heavy Fuel Oil',
    'Other Liquid Biofuels']
SOLID_TYPES = [
    ('Wood and products of wood and cork (except furniture); '
        'articles of straw and plaiting materials (20)'),
    'Coke Oven Coke']
DISTRIBUTION_GAS='Distribution services of gaseous fuels through mains'
GAS_TYPES = [
    DISTRIBUTION_GAS,
    'Biogas']
DISTRICT_SERVICE_LABEL = 'Steam and hot water supply services'

BIOGASOLINE = 'Biogasoline'
BIODIESEL = 'Biodiesels'
MOTORGASOLINE = 'Motor Gasoline'
GAS_DIESEL_OIL = 'Gas/Diesel Oil'
FUELS = [BIODIESEL, GAS_DIESEL_OIL, MOTORGASOLINE, BIOGASOLINE]

MOTOR_VEHICLES = 'Motor vehicles, trailers and semi-trailers (34)'
# the spelling mistake in accessories in the following LABEL is intended as that's how it is 
# in the csv tables
SALE_REPAIR_VEHICLES = ('Sale, maintenance, repair of motor vehicles, motor vehicles parts, '
    'motorcycles, motor cycles parts and accessoiries')

WOOD_PRODUCTS=('Wood and products of wood and cork (except furniture); '
    'articles of straw and plaiting materials (20)')

NORTH = ['Denmark', 'Finland', 'Sweden', 'Norway', 'Iceland']

WEST = ['Austria', 'Belgium', 'Germany', 'Spain', 'France', 'Ireland',
        'Italy', 'Luxembourg', 'Malta', 'Netherlands',
        'Portugal', 'United Kingdom', 'Switzerland', 'Liechtenstein']

EAST = ['Bulgaria', 'Cyprus', 'Czechia', 'Estonia', 'Greece',
        'Hungary', 'Croatia', 'Lithuania', 'Latvia', 'Poland',
        'Romania', 'Slovenia', 'Slovakia', ]

class UserContext:
    """
    LIST of originally adjustable variables
  
    All values have defaults apart from the ones with
    required. So the minimum data required by the user for the
    baseline is filling in the required data.

    I don't know how to make it so that the default variables are loaded and can then be changed
    by the user.
    I think it would be necessary to recall the data from the server after the first consumption
    calculations screen.
    """

    ## Baseline variables ##

    year = int(2022)   # required
    region = str()   # required - Equivalent to "name the project"
    # I ask this to differentiate between policies, but maybe the tool has another way.
    policy_label = str()
    country = str()   # Required
    ab = str()      # This can be combined with the one above

    target_area = str()  # Required #3 options in dropdown menu
    area_type = str()   # Required #4_options in drop down menu - mixed, rural, city, town
    pop_size = int()  # Required - completely open


    house_size = float()  # completely open, but with a default value.
    income_level = str()  # There are 5 options in a drop down menu

    eff_scaling = float()  # default value should be 0.97 (equivalent to 3 %)

    # the following baseline variables are now set to defaults, but are still here for completion
    river_prop = float()
    ferry_prop = float()
    rail_prop = float()
    # These values should sum to 1 (or 100 %) They all have a default value
    bus_prop = float()

    ## end of baseline variables ##

    # For the policies, the following additional questions are required (as well as those above)
    ## policy variables ##
    policy_year = int()   # required - This question has been missed in the UI


    eff_gain = str()     # required
    eff_scaler = float()

    local_electricity = str()
    el_type = str()  # 3 options from drop_down menu
    el_scaler = float()

    s_heating = str()  # required

    biofuel_takeup = str()  # required
    bio_scaler = float()

    ev_takeup = str()  # required
    ev_scaler = float()

    modal_shift = str()  # required
    ms_fuel_scaler = float()
    ms_pt_scaler = float()
    ms_veh_scaler = float()

    new_floor_area = float()  # default is zero

    # These are all to do with electricity mix 99% of time should use default values
    hydro_prop = float()
    solar_pvc_prop = float()
    coal_prop = float()
    gas_prop = float()
    nuclear_prop = float()
    wind_prop = float()
    petrol_prop = float()
    solar_thermal_prop = float()
    tide_prop = float()
    geo_prop = float()
    # Last electricity mix  #These values should sum to 1 (or 100 %)
    nec_prop = float()

    district_prop = float()
    electricity_heat_prop = float()
    combustable_fuels_prop = float()    # These 3 values should sum to 1 (or 100 %)

    liquids_prop = float()
    solids_prop = float()
    gases_prop = float()                # These 3 values should sum to 1 (or 100 %)

    direct_district_emissions = float()  # A default value os given.

    ## end of policy variables ##

    def __init__(self, year, country, pop_size, region=country):
        self.year = year
        self.country = country  # TODO: straighten out regions and countries
        self.pop_size = pop_size
        self.region = region
        self.demand_kv = None  # TODO: set correct type (empty pd dictionary)

    # Policy "functions"
    # The different Policies are written as functions to reduce the length of the calculation code

    def biofuels(self, scaler):
        """
        This is a policy.

        *Explanation*

        This sort of policy acts only on the Expenditure (Intensities don't change)
        Similar polices could exist for housing fuel types, ...
        Similar adjustments to this could also be needed to correct the baselines if the user knows the
        results to be different

        Local Inputs:
        - demand_kv[BIOGASOLINE]
        - demand_kv[BIODIESEL]
        - demand_kv[MOTORGASOLINE]
        - demand_kv[GAS_DIESEL_OIL]

        Outputs:
        - demand_kv[BIOGASOLINE] - careful, this means this field is permanently changed after call
        - demand_kv[BIODIESEL] - careful, this means this field is permanently changed after a call
        - demand_kv[MOTORGASOLINE] - careful, this means this field is permanently changed after a call
        - demand_kv[GAS_DIESEL_OIL] - careful, this means this field is permanently changed after a call
        """
        demand_kv = self.demand_kv  # shortcut to work on this field

        #
        # current_biofuels = demand_loc_KV['Biogasaline'] + demand_loc_KV['biodiesel'] /

        # Step 1. Determine current expenditure on fuels and the proportions of each type
        total_fuel = demand_kv[BIOGASOLINE] + demand_kv[BIODIESEL] + \
            demand_kv[MOTORGASOLINE] + demand_kv[GAS_DIESEL_OIL]
        diesel = (demand_kv[BIODIESEL] + demand_kv[GAS_DIESEL_OIL])
        petrol = (demand_kv[MOTORGASOLINE] + demand_kv[BIOGASOLINE])

        # Step 1.1 current_biofuels = (demand_kv[BIOGASOLINE] + demand_kv[BIODIESEL]) / total_fuel

        # Step 2. Increase the biofuel to the designated amount
        demand_kv[BIOGASOLINE] = scaler * total_fuel * (petrol / (diesel + petrol))
        demand_kv[BIODIESEL] = scaler * total_fuel * (diesel / (diesel + petrol))

        # Step 3. Decrease the others by the correct amount, taking into account their initial values
        # The formula to do this is :
        # New Value = Remaining_expenditure * Old_proportion (once the previous categories are removed)
        # This can't be more than the total! - TODO: assert?
        sum_changed = demand_kv[BIOGASOLINE] + demand_kv[BIODIESEL]

        if sum_changed > total_fuel:
            # TODO: exception
            pass

        demand_kv[MOTORGASOLINE] = (
            total_fuel - sum_changed) * (petrol / (diesel + petrol))
        demand_kv[GAS_DIESEL_OIL] = (
            total_fuel - sum_changed) * (diesel / (diesel + petrol))


def electric_vehicles(demand_kv, scaler):
    """
    This is a policy.

    *Explanation*

    xx% of vehicles are ev
    First we reduce the expenditure on all forms of transport fuels by xx%
    Then, we need to add something onto the electricity

    For this we need to: calculate how much fuel is saved and convert it back into Liters
    (and then kWh)
    Take into account the difference in efficiency between the two types
    Add the kWh evenly onto the electricity sectors

    Explanation/Description
    This sort of policy acts only on the Expenditure 

    Local Inputs:
    - demand_kv[BIODIESEL]
    - demand_kv[GAS_DIESEL_OIL]
    - demand_kv[MOTORGASOLINE]
    - demand_kv[BIOGASOLINE]
    - demand_kv[ELECTRICITY_TYPES]

    Global Inputs:
    - country - string of a country name
    - FUEL_PRICES_T.loc['Diesel_2020', country]
    - FUEL_PRICES_T.loc['petrol_2020', country]
    - ELECTRICITY_TYPES

    Outputs:
    - demand_kv[electricity] - careful, this means this (these) field is permanently changed after a call to this method

    """

    # Step 1 Assign a proportion of the fuels to be converted and reduce the fuels by the correct amount

    diesel = (demand_kv[BIODIESEL] + demand_kv[GAS_DIESEL_OIL])*scaler
    petrol = (demand_kv[MOTORGASOLINE] + demand_kv[BIOGASOLINE])*scaler

    for fuel in FUELS:
        demand_kv[fuel] = demand_kv[fuel]*(1-scaler)

    # Step 2 Turn the amount missing into kWh
    diesel /= FUEL_PRICES_T.loc['Diesel_2020', country]
    petrol /= FUEL_PRICES_T.loc['petrol_2020', country]

    diesel *= 38.6*0.278   # liters, then kWh
    petrol *= 34.2*0.278   # liters, then kWh

    # Step 3. #Divide that amount by 4.54 (to account foe the efficiency gains)
    diesel /= 4.54         # Efficiency saving
    petrol /= 4.54         # Efficiency saving

    # Step 4. Assign this to increased electricity demand
    elec_vehicles = diesel + petrol
    elec_total = demand_kv[ELECTRICITY_TYPES].sum()
    elec_scaler = (elec_vehicles + elec_total) / elec_total

    demand_kv[ELECTRICITY_TYPES] *= elec_scaler


def eff_improvements(demand_kv, scaler):
    """
    This is a policy.

    *Explanation*

    Retrofitting reduces energy expenditure on heating by xx %

    This sort of policy acts only on the Expenditure (intensities don't change)
    Take the expenditure on household fuels and reduce it by a scale factor defined by the user

    Global Inputs:
    - district - label
    - liquids
    - solids
    - gases
    - electricity - set of labels/strings marking electricity entries in demand_kv
    - ad["elec_water"]
    - ad["elec_heat"]
    - ad["elec_cool"]
    - district

    Local Inputs:
    - demand_kv <- all liquids, solids, and gases, electricity entries
    - demand_kv[GAS_DIESEL_OIL]
    - demand_kv[MOTORGASOLINE]
    - demand_kv[BIOGASOLINE]
    - demand_kv[electricity] - seems this time to be a list of values (as later sum used)

    Outputs:
    - demand_kv[district] - not sure if this is a side effect or not

    """

    # Step 1. This can be done as a single stage.
    # Just reduce the parts that can be reduced by the amount in the scaler

    for liquid in LIQUID_TYPES:
        demand_kv[liquid] = (demand_kv[liquid] * (1 - scaler))

    for solid in SOLID_TYPES:
        demand_kv[solid] = (demand_kv[solid] * (1 - scaler))

    for gas in GAS_TYPES:
        demand_kv[gas] = (demand_kv[gas] * (1 - scaler))

    for elec in ELECTRICITY_TYPES:
        elec_hold = demand_kv[elec] * (1 - (adjustable_amounts["elec_water"] + adjustable_amounts["elec_heat"] +
                                       adjustable_amounts["elec_cool"]))  # Parts not related to heating/cooling etc
        demand_kv[elec] = (demand_kv[elec] * (adjustable_amounts["elec_water"] +
                           adjustable_amounts["elec_heat"] + adjustable_amounts["elec_cool"]) * (1-scaler))
        demand_kv[elec] += elec_hold

    demand_kv[DISTRICT_SERVICE_LABEL] = demand_kv[DISTRICT_SERVICE_LABEL] * \
        (1-scaler)


def transport_modal_shift(demand_kv, scaler, scaler_2, scaler_3):
    """
    This is a policy.

    *Explanation*

    Modal share - decrease in private transport and increase in public transport

    This sort of policy acts only on the Expenditure (Intensities don't change)
    The expenditure on private transport is reduced by a certain amount (1 part for fuels and 1 for vehicles)

    The public transport is also increased by a different amount. This is to account for the effects of active travel

    Global Inputs:
    - public_transport - list of labels TODO: public_transport is nowhere defined

    Local Inputs:
    - demand_kv[GAS_DIESEL_OIL]
    - demand_kv[MOTORGASOLINE]
    - demand_kv[BIOGASOLINE]
    - demand_kv[electricity] - seems to be a list of values (as later sum used)
    - demand_kv[MOTOR_VEHICLES]
    - demand_kv[SALE_REPAIR_VEHICLES]
    - demand_kv <- for all public_transports 

    Outputs:
    - demand_kv[MOTOR_VEHICLES] - careful, this means this field is permanently changed after a call to this method
    - demand_kv[SALE_REPAIR_VEHICLES] - - careful, this means this field is permanently changed after a call to this method
    - demand_kv <- for all public_transports - careful, this means this field is permanently changed after a call to this method

    """

    for fuel in FUELS:
        demand_kv[fuel] *= (1-scaler)
        # In this case, we also assume that there is a reduction on the amount spent on vehicles
        # Change in modal shift takes vehicles off the road?

    for vehicle in [MOTOR_VEHICLES, SALE_REPAIR_VEHICLES]:
        demand_kv[vehicle] *= (1-scaler_3)

    for transport in public_transport:  # Public transport was defined above
        demand_kv[transport] *= (1+scaler_2)


def local_generation(ab_M, demand_kv, scaler, type_electricity):
    """
    This is a policy.

    *Explanation*

    Local electricity is produced by (usually) rooftop solar and it is utilized only in that area

    Reduce current electricity by xx %
    Introduce a new electricity emission intensity (based on PV in the LCA emission intensities) 
    that accounts for the missing xx %    

    Global Inputs:
    - direct_ab
    - indirect_ab
    - electricity: here it's used a field of labels again

    Local Inputs:
    - demand_kv[ELECTRICITY_NEC]
    - M_countries_LCA.loc[direct_ab:indirect_ab,type_electricity]


    Outputs:
    - ab_M.loc[direct_ab:indirect_ab,ELECTRICITY_NEC]
    - demand_kv[ELECTRICITY_NEC] - careful, this means this field is permanently changed after a call to this method

    """

    elec_total = demand_kv[ELECTRICITY_TYPES].sum()

    for elec in ELECTRICITY_TYPES:

        demand_kv[elec] = (demand_kv[elec] * (1 - scaler))

    # Assign the remaining amount to the spare category (electricity nec)
    demand_kv[ELECTRICITY_NEC] = elec_total * scaler

    # Set the emission intensity of this based on LCA values
    ab_M.loc[direct_ab:indirect_ab,
             ELECTRICITY_NEC] = EMISSION_COUNTRIES_LCA_T.loc[direct_ab:indirect_ab, type_electricity]


def local_heating(ab_m, demand_kv, district_prop, elec_heat_prop,
                  combustable_fuels_prop, liquids_prop, gas_prop, solids_prop, district_val):
    """
    Is this a policy? It has a lot of nice input values.

    THIS JUST REPEATS BASELINE QUESTIONS 9 - 10.
    ALLOWING THE USER TO CHANGE THE VALUES

    Global Inputs:
    - district
    - direct_ab
    - total_fuel
    - electricity: here it's used a field of labels again
    - ad["elec_water"]
    - ad["elec_heat"]
    - ad["elec_cool"]
    - elec_total
    - liquids
    - solids

    Local Inputs:
    - demand_kv[elec] for all labels in electricity
    - demand_kv[liquid] for all labels in liquids

    Outputs:
    - demand_kv[elec] for all labels in electricity. Careful, this means these fields are permanently changed after a call to this method
    - demand_kv[liquid] for all labels in liquids. Careful, this means these fields are permanently changed after a call to this method
    - demand_kv[WOOD_PRODUCTS]
    - demand_kv[DISTRIBUTION_GAS]
    - ab_M.loc[direct_ab,district] - careful, this means this field is permanently changed after a call to this method

    """

    # DISTRICT HEATING
    demand_kv[DISTRICT_SERVICE_LABEL] = total_fuel * district_prop

    # ELECTRICITY
    for elec in ELECTRICITY_TYPES:
        # determine amount of each electricity source in total electricity mix.
        prop = demand_kv[elec] / elec_total
        elec_hold = (1 - (adjustable_amounts["elec_water"]
                          + adjustable_amounts["elec_heat"]
                          + adjustable_amounts["elec_cool"])
                     ) * demand_kv[elec]  # electricity for appliances
        # TODO: verify, that local elec_heat_prop works here
        # Scale based on electricity use in heat and elec mix
        demand_kv[elec] = prop * elec_heat_prop * total_fuel / elec_price
        demand_kv[elec] += elec_hold  # Add on the parts to do with appliances

    for liquid in LIQUID_TYPES:
        liquids_sum = demand_kv[LIQUID_TYPES].sum()
        if liquids_sum != 0:
            # Amount of each liquid in total liquid expenditure
            prop = demand_kv[liquid] / liquids_sum
            demand_kv[liquid] = prop * liquids_prop * \
                combustable_fuels_prop * total_fuel
        else:
            demand_kv['Kerosene'] = liquids_prop * \
                combustable_fuels_prop * total_fuel

    for solid in SOLID_TYPES:
        solids_sum = demand_kv[SOLID_TYPES].sum()
        if solids_sum != 0:
            # Amount of each solid in total solid expenditure
            prop = demand_kv[solid] / solids_sum
            demand_kv[solid] = prop * solids_prop * \
                combustable_fuels_prop * total_fuel
        else:
            demand_kv[WOOD_PRODUCTS] = solids_prop * \
                combustable_fuels_prop * total_fuel

    for gas in GAS_TYPES:
        gasses_sum = demand_kv[GAS_TYPES].sum()
        if gasses_sum != 0:
            # Amount of each gas in total gas expenditure
            prop = demand_kv[gas] / gasses_sum
            demand_kv[gas] = prop * gases_prop * \
                combustable_fuels_prop * total_fuel

        else:
            demand_kv[DISTRIBUTION_GAS] = gases_prop * \
                combustable_fuels_prop * total_fuel

    # The 'direct_ab' value should be changed to the value the user wants.
    # The user needs to convert the value into kg CO2e / Euro
    # 1.0475 # USER_INPUT
    ab_m.loc[direct_ab, DISTRICT_SERVICE_LABEL] = district_val


###################### end of policy methods/functions  ##########################################


# Construction Emissions new part. 

# This answers the question on the first policy page 
# 2. Construction 
# 2.1 New planned residential buildings in total gross square meters, m2"

# Baseline Version Peeter planner

# Baseline calculation here (policies is essentially the same calculation)
########### Explanation #######################
# The calculations work by describing the economy as being
# composed of 200 products, given by 'products'.
# For each product there is an emission intensity and they are collected
# together in ab_M.
# There are separate emission intensities for the 'direct production'
# and the 'indirect production' (rest of the supply chain).
# So ab_M is a 200 x 2 table.
# Some products that describe household fuel use for heat and
# also transport fuel use for cars have another emission
# intensity as well. These are held in separate tables
# 'use_phase' and 'tail_pipe' (all other products have 0 here)

# To calculate the emissions, each value in ab_M + the values in use_phase
# and tail_pipe are multiplied by the amount the household spends
# on each of the 200 products. These are stored in another table
# called demand_kv (demand vector).
# The emissions for each product from the direct production,
# indirect production, and use_phase/tail_pipe are summed
# to get the total emissions for that product.

# Once we have the total emissions for each product for that year,
# they are grouped together into 'sectors' that describe different things.
# There are 7 in total:
# Household Energy, Household Other, transport fuels, transport other, air transport, food,
# tangible goods, and services

# The calculations are performed every year until 2050,
# with the values of demand_kv and ab_M changing slighting each year.
# This is based on 3 factors, efficiency improvements,
# changes in income and changes in household size. There is also a
# section where these projections can change as a result
# of different policies (for the baseline no policies are introduced)

###################################################################################
# Determine Emissions for all years

######## Included in the start screen ##############################

def calculate_consumption(year, region, country, country_abbr):
    ################ Question 9.0 ##################################
    year = 2022  # baseline year
    region = "County_Meath"  # User_input

    # U9.1
    # This is just a label for the policy. Or the tool has a way to select different policies.
    policy_label = "BL"

    # U9.0
    country = "Ireland"  # This is to choose the country - USER_INPUT
    ab = "IE"            # This is to identify the country, should match above

    # Population_size
    pop_size = 195000  # USER_INPUT

    # now create a local variable with name "pop_size" + Policy_label
    # here in this example it would be equivalent to
    # pop_sizeBL = pop_size
    # TODO: check what this could be used for later
    # create local variable with name "pop_size" + Policy_label
    locals()["pop_size" + policy_label] = pop_size

    ##################################################################################
    # Additional questions for the baseline
    # For a simple example, we use defaults for all of them

    # U9.2
    # This is to select the demand vector - the user should choose
    U_type = "average"  # 'average', 'town', 'city', 'rural'

    # Extracting the correct demand vector - this is the initialization of demand_kv
    # TODO: why is that pumped through locals?
    # if U_type is average, this is: Y_average[country].copy()
    demand_kv = locals()["Y_" + U_type][country].copy()

    # U9.3: House_size - also extracted
    # This is the default
    House_size_ab = HOUSE_SIZE_T.loc['Average_size_' + U_type, country]
    # House_size_ab = 2.14 #xx###USER_INPUT would look like this here

    # U9.4:Income_scaler
    # options are "1st_household" , "2nd_household", "3rd_household", "4th_household", "5th_household"
    # 1st household is the richest.
    Income_choice = "3rd_household"
    # Otherwise,  the user selects the income level of the household (they choose by quintiles)
    Income_scaler = INCOME_SCALING_T.loc[Income_choice, country] / \
        INCOME_SCALING_T.loc['Total_household', country]  # USER_INPUT
    Elasticity = 1  # Random number for now. It should be specific to country and product

    # if Income_choice == "3rd_household":
    #    Income_scaler = 1

    demand_kv *= Income_scaler * Elasticity
    ##############################################################################################

    # U9.5: This is the expected global reduction in product emissions
    # Suggestion - Just give the user one of three options, with the default being normal

    fast = 0.07
    normal = 0.03
    slow = 0.01

    eff_scaling = 1 - normal  # USER_INPUT

    ##############################################################
    # Forming data for the calculations
    # These are needed for holding the results
    DF = pd.DataFrame(np.zeros((30, 8)), index=list(range(2020, 2050)),
                      columns=IW_SECTORS_T.columns)  # Holds final data in sectors 7 (+ sum)

    DF_tot = pd.DataFrame(np.zeros((30, 200)), index=list(range(2020, 2050)),
                          columns=PRODUCT_COUNT)  # holds final data in products (200)

    DF_area = pd.DataFrame(np.zeros((30, 8)), index=list(range(2020, 2050)),
                           columns=IW_SECTORS_T.columns)  # Holds area emissions (multiplies by pop_size

    direct_ab = "direct_"+ab
    indirect_ab = "indirect_"+ab
    # TODO: is this doing anything - not assigned! -> just debugging?
    EMISSION_COUNTRIES_T.loc[direct_ab:indirect_ab, :].copy()

    # Here the emission intensities are selected
    emission_intensities = locals(
    )[ab + "_M"] = EMISSION_COUNTRIES_T.loc[direct_ab:indirect_ab, :].copy()

    # These are needed for the use phase emissions
    Tail_pipe_ab = TAIL_PIPE_T[country].copy()
    Use_phase_ab = USE_PHASE_T[country].copy()

    # This is needed for calculating the amount of electricity coming from heating
    adjustable_amounts = ADJUSTABLE_AMOUNTS_T[country].copy()
    elec_price = ELECTRICITY_PRICES_T[country]["BP_2019_S2_Euro"]

    # Baseline Modifications go here  ##Possibly not included in this version of the tool###########
    ################ end of the mandatory questions #######################

    elec_total = demand_kv[ELECTRICITY_TYPES].sum()

    # TODO: consider moving this somewhere else
    electricity_heat = (adjustable_amounts["elec_water"] + adjustable_amounts["elec_heat"] +
                        adjustable_amounts["elec_cool"]) * elec_total * elec_price

    total_fuel = demand_kv[SOLID_TYPES].sum() + demand_kv[LIQUID_TYPES].sum(
    ) + demand_kv[GAS_TYPES].sum() + demand_kv[DISTRICT_SERVICE_LABEL].sum() + electricity_heat
    # TODO: look at this later -> we assume all 'fuels' are the same efficiency (obviously wrong, but no time to fix)


baseline = calculate_consumption(year=2022, region="Ireland") # TODO: continue

##Basic policy questions go here######################################

# Here, we are essentially just asking the questions we asked for the BL again. The problem is that before the
# policy year (in this case 2025), the values should be equal to the baseline. So I have just redefined the variables
# here. But for the tool if all variables are predefined and then sent to a function to run the calculation, would they
# need to be new variables?

# Question 10:
# U10.1
policy_year = 2025  # USER_INPUT

# U10.2
# Population_size
pop_size_policy = 205000  # USER_INPUT


##############################################
#     NEW PART FOR THE CONSTRUCTION EMISSIONS!
#######################################################
## Construction emissions#############################################################################################

##U 10.3#############################################

new_floor_area = 0   # USER_INPUT
# END OF PART FOR THE CONSTRUCTION EMISSIONS!


###############################################################
#############The actual calculation starts here################
###############################################################

# Scale factor applied to income - unique value for each decade
income_scaling = INCOME_PROJ_T.loc[country]
# Scale factor applied to household size - unique value for each decade
house_scaling = HOUSE_SIZE_PROJ_T.loc[country]

# Questions should be asked in this order! Some depend on the results of others
EFF_gain = False  # USER_INPUT U11.1.0
EFF_scaler = 0.5  # USER_INPUT   U11.1.1
local_electricity = False  # USER_INPUT  U11.2.0
# USER_INPUT U11.2.1  'Electricity by solar photovoltaic','Electricity by biomass and waste','Electricity by wind','Electricity by Geothermal'
el_type = 'Electricity by solar photovoltaic'
el_scaler = 0.5  # User_Input U11.2.2

s_heating = False  # USER_INPUT   U11.3.0

# the following are already defined
# district_prop = 0.25 #USER_INPUT  U11.3.1
# electricity_heat_prop = 0.75 #USER_INPUT
# combustable_fuels_prop = 0.25 #USER_INPUT

# solids_prop = 0.0 #USER_INPUT   U11.3.2
# gases_prop = 0.0 #USER_INPUT
# liquids_prop = 0.0 #USER_INPUT


# District_value = ab_M.loc[direct_ab,district].sum()# ab_M   0.0 # USER_INPUT  U11.3.3

biofuel_takeup = False  # USER_INPUT  U12.1.0
bio_scaler = 0.5  # USER_INPUT      U12.1.1

ev_takeup = False  # USER_INPUT  U12.2.0
ev_scaler = 0.5  # User_Input U12.2.1

modal_shift = False  # USER_INPUT U12.3.0
ms_fuel_scaler = 0.5  # USER_INPUT U12.3.1
ms_veh_scaler = 0.5  # USER_INPUT U12.3.2
ms_pt_scaler = 0.2  # USER_INPUT U12.3.3


for year_it in range(year, 2051):  # baseline year to 2050 (included)

    # check the policy part

    # if year_it == 2020:

    #     income_mult = 1 # This is just for the year 2020
    #     house_mult = 1  # This is just for the year 2020
    #     eff_factor = 1  # This is just for the year 2020

    ###########Policies are from here################################################################
    if policy_label != "BL" and year_it == policy_year:  # & policy_label != "BL":

        #demand_kv = demand_kv_policy
        # house_size_ab = house_size_ab_policy  #Because we are not asking these questions
        pop_size = pop_size_policy

        ##############Household Efficiency###################################################

        if EFF_gain:
            eff_improvements(demand_kv, EFF_scaler)

        ##############Local_Electricity########################################################################################
        ######################U11.2######################################

        if local_electricity:
            local_generation(emission_intensities,
                             demand_kv, el_scaler, el_type)

        if s_heating:
            local_heating(emission_intensities, demand_kv, district_prop, electricity_heat_prop,
                          combustable_fuels_prop, liquids_prop, gases_prop, solids_prop, District_value)

        ###########Biofuel_in_transport########################################################################################
        ########### U12.1##############

        if biofuel_takeup:
            biofuels(demand_kv, bio_scaler)

        ########Electric_Vehicles##################################################################################################
        ###### U12.2#############

        if ev_takeup:
            electric_vehicles(demand_kv, ev_scaler)

        #########Modal_Shift#######################################################################################################
        #########U12.3#################

        if modal_shift:
            transport_modal_shift(demand_kv, ms_fuel_scaler,
                                  ms_pt_scaler, ms_veh_scaler)

    if year_it > 2020 and year_it <= 2030:
        # Select the income multiplier for this decade
        income_mult = income_scaling['2020-2030']
        # Select the house multiplier for this decade
        house_mult = house_scaling['2020-2030']
        eff_factor = eff_scaling

    if year_it > 2030 and year_it <= 2040:
        # Select the income multiplier for this decade
        income_mult = income_scaling['2030-2040']
        # Select the house multiplier for this decade
        house_mult = house_scaling['2030-2040']
        eff_factor = eff_scaling

    if year_it > 2040 and year_it <= 2050:
        # Select the income multiplier for this decade
        income_mult = income_scaling['2040-2050']
        # Select the house multiplier for this decade
        house_mult = house_scaling['2040-2050']
        eff_factor = eff_scaling

    demand_kv *= income_mult

    emission_intensities *= eff_factor

    Use_phase_ab *= eff_factor

    Tail_pipe_ab *= eff_factor

    # Then we have to recalculate
    # GWP: Global Warming Potential (could be also called Emissions)

    GWP_ab = pd.DataFrame(emission_intensities.to_numpy().dot(
        np.diag(demand_kv.to_numpy())))  # This is the basic calculation
    GWP_ab.index = ['direct', 'indirect']
    GWP_ab.columns = PRODUCT_COUNT
    # This adds in the household heating fuel use
    Use_phase_ab_GWP = demand_kv * Use_phase_ab
    # This adds in the burning of fuel for cars
    Tail_pipe_ab_GWP = demand_kv * Tail_pipe_ab
    # This puts together in the same table (200 x 1)
    Total_use_ab = Tail_pipe_ab_GWP.fillna(0) + Use_phase_ab_GWP.fillna(0)
    # all of the other 200 products are zero
    # Put together the IO and use phase
    GWP_ab.loc['Use phase', :] = Total_use_ab

    #GWP_EE_pc = GWP_EE/House_size_EE
    # print(year_it)

    #GWP_EE = GWP_EE * (eff_factor) * (income_mult)
    GWP_ab_pc = GWP_ab / (House_size_ab * house_mult)

    # Put the results into sectors
    DF.loc[year_it] = IW_SECTORS_NP_TR_T.dot(GWP_ab_pc.sum().to_numpy())
    DF_tot.loc[year_it] = GWP_ab_pc.sum()
    DF_area.loc[year_it] = IW_SECTORS_NP_TR_T.dot(
        GWP_ab_pc.sum().to_numpy()) * pop_size

DF['Total_Emissions'] = DF.sum(axis=1)
DF_area['Total_Emissions'] = DF_area.sum(axis=1)


###########################################################################################################
# New Construction Emissions part!
#################################################################################################################

if policy_label != "BL":
    if country in NORTH:
        Building_Emissions = 350 * new_floor_area/pop_size

    if country in WEST:
        Building_Emissions = 520 * new_floor_area/pop_size

    if country in EAST:
        Building_Emissions = 580 * new_floor_area/pop_size

    DF.loc[policy_year, 'Total_Emissions'] += Building_Emissions
    DF_area.loc[policy_year,
                'Total_Emissions'] += Building_Emissions * pop_size


##############################################################################################################
# End of Construction Emissions part!
#############################################################################################################
# Adding total emissions by multiplying by population


# F_tot.columns = Exio_products
locals()[region + "_Emissions_" + policy_label] = DF
locals()[region + "_Emissions_tot_" + policy_label] = DF_tot

locals()[region + "_Area_Emissions_" + policy_label] = DF_area

# Graphs are from here

# First Graph is a breakdown of the Emissions as a stacked bar graph. Maybe best to just show this one by itself?

# Describe Emissions over time
# The construction Emissions are now shown here. I just added very quickly so please make better!

fig, ax = plt.subplots(1, figsize=(15, 10))
# Name of country Emissions
country = "County_Meath"
policy_label = "BL"

DF = locals()[country + "_Emissions_" + policy_label].copy()

###
#x = np.arange(list(range(2020,2050)))
# plot bars

Labels = ['HE', 'HO', 'TF', 'TO', 'AT', 'F', 'TG', 'S']
sectors = list(IW_SECTORS_T.columns)

bottom = len(DF) * [0]
for idx, name in enumerate(sectors):
    plt.bar(DF.index, DF[name], bottom=bottom)
    bottom = bottom + DF[name]

plt.bar(DF.index, DF['Total_Emissions'], edgecolor='black', color='none')

ax.set_title("Annual Household Emissions for %s" % country, fontsize=20)
ax.set_ylabel('Emissions / kG CO2 eq', fontsize=15)
ax.tick_params(axis="y", labelsize=15)
ax.set_xlabel('Year', fontsize=15)
ax.tick_params(axis="x", labelsize=15)

ax.legend(Labels, bbox_to_anchor=([1, 1, 0, 0]), ncol=8, prop={'size': 15})


plt.show()


# Clicking on a bar or looking at a comparison between policies should generate this second graph
# The labels below are just for different policies.

# There should also be an option to remove the total emissions part (This is basically only useful for new areas)


# Now_make_graphs_of these

width = 0.2
x = np.arange(len(County_Meath_Emissions_BL.columns))

fig, ax = plt.subplots(figsize=(15, 10))

rects1 = ax.bar(
    x + 0 * width, County_Meath_Emissions_BL.loc[2025], width, label='BL')
# Extra policies
rects2 = ax.bar(x - 1.5 * width,
                County_Meath_Emissions_P1.loc[2025], width, label='P1')
# Extra Policies
rects3 = ax.bar(x + 1.5 * width,
                County_Meath_Emissions_P2.loc[2025], width, label='P2')
# rects4 = ax.bar(x - width / 2, Berlin_Emissions_NA.loc[2025], width, label='NA')  # Extra Policies


#plt.bar(x_sectors, E_countries_GWP_sectors_pp['EE'], width = 0.5,  color='green')
#plt.bar(x_sectors, E_countries_GWP_sectors_pp['FI'], width = 0.5, color='blue', alpha = 0.5)
ax.legend_size = 20
ax.set_ylabel('Emissions / kG CO2 eq', fontsize=20)
ax.set_xlabel('Emissions sector', fontsize=20)
ax.set_title(
    'Per capita emissions by sector for County Meath policies', fontsize=25)
ax.set_xticks(x)
ax.set_xticklabels(County_Meath_Emissions_BL.columns, fontsize=15)
#ax.set_yticklabels( fontsize = 15)
ax.tick_params(axis="y", labelsize=15)
ax.legend(prop={'size': 15})


#x.label(rects1, padding=3)
#x.label(rects2, padding=3)

# lt.xlabel("Sectors")
#lt.ylabel("CO2 eq /  kG?")
#lt.title("Global Emissions by Sector")

plt.xticks(x, County_Meath_Emissions_BL.columns, rotation=90)

#plt.savefig("Sectoral_Graphs_breakdown.jpg",bbox_inches='tight', dpi=300)


plt.show()

# Finally, there should be some sort of cumulative emissions measurement. Ths is also important in the case of delaying policies

# This calculates the different cumulative emissions
# Policy_labels = ["BL", "MSx50", "SHx50", "EVx50", "NA", "ALLx50_2035", "ALLx50_2025"]   #THIS is just all the policies I made
Policy_labels = ["BL", "P1", "P2"]
# Policy_labels = ["BL", "RFx50_2025", "RFx50_2035"]#for the graphs
region = "County_Meath"
for policy in Policy_labels:

    locals()[region + "_summed_" + policy] = pd.DataFrame(np.zeros((30, 1)),
                                                          index=list(range(2020, 2050)), columns=["Summed_Emissions"])

    locals()[region + "_summed_" + policy].loc[2020, "Summed_Emissions"] = locals()[
        region + "_Emissions_" + policy].loc[2020, 'Total_Emissions']
    years = list(range(2020, 2050))
    for year in years:
        locals()[region + "_summed_" + policy].loc[year+1, "Summed_Emissions"] = locals()[region + "_summed_" +
                                                                                          policy].loc[year, "Summed_Emissions"] + locals()[region + "_Emissions_" + policy].loc[year+1, 'Total_Emissions']

    print("The Emissions in 2025 for %s is" % policy, locals()[
          region + "_Emissions_" + policy].loc[2025, 'Total_Emissions'])


# Make the graph

# Describe Emissions over time


fig, ax = plt.subplots(1, figsize=(15, 10))
# Name of country Emissions
country = "County_Meath"
# Policy_labels = ["BL","EVx50", "MSx50", "SHx50", "NA"]
Policy_labels = ["BL", "P1", "P2"]


counter = 0
for policy in Policy_labels:
    DF = locals()[country + "_summed_" + policy].copy()

    ###
    #x = np.arange(list(range(2020,2050)))
    # plot bars

    #Labels = ['HE','HO','TF','TO','AT','F','TG','S']
    sectors = list(IW_SECTORS_T.columns)

    #bottom = len(DF) * [0]
    # for idx, name in enumerate(sectors):
    #   plt.bar(DF.index, DF[name], bottom = bottom)
    #  bottom = bottom + DF[name]

    plt.plot(DF.index, DF.Summed_Emissions, )

    plt.fill_between(DF.index, DF.Summed_Emissions, alpha=0.4)  # +counter)

    counter += 0.1

#x = np.arange(len(Ireland_Emissions.index))
#width = 0.8

#rects1 = ax.bar(x, Ireland_Emissions['Housing_Energy'], width, label=ab)

ax.set_title("Aggregated per capita Emissions for %s 2020-2050" %
             country, fontsize=20)
ax.set_ylabel('Emissions / kG CO2 eq', fontsize=15)
ax.tick_params(axis="y", labelsize=15)
ax.set_xlabel('Year', fontsize=15)
ax.tick_params(axis="x", labelsize=15)

ax.legend(Policy_labels, loc='upper left', ncol=2, prop={'size': 15})

#plt.savefig("Cumulative_example_high_buildphase.jpg",bbox_inches='tight', dpi=300)


plt.show()

print("County_Meath_Emissions_P1", County_Meath_Emissions_P1)

print("County_Meath_Emissions_P4", County_Meath_Emissions_P4)
