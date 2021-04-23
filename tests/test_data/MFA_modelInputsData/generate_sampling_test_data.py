# generate test_data
# Last date : 20.04.2021
# By : Matthias Mattanovich (matmat@biosustain.dtu.dk)
# This script is intended to generate sample data and save them into the
# test_data file. The saved objects will then be used to test the
# MFA_sampling functions using unit testing.
import pickle
import pandas as pd
import pathlib
import cobra
from BFAIR.INCA import INCA_reimport
from BFAIR.INCA.sampling import (
    add_constraints,
    find_biomass_reaction,
    get_min_solution_val,
    replace_biomass_rxn_name,
    add_feasible_constraints,
    reshape_fluxes_escher,
    bound_relaxation,
)

current_dir = str(pathlib.Path(__file__).parent.absolute())

pd.set_option("mode.chained_assignment", None)
# Use pickle to save python variables
filehandler = open("sampling_test_data.obj", "wb")


def get_bounds_df(model):
    # Helper function to have a way to compare the bounds
    bounds_temp = {}
    # Round to 5 decimal places to avoid issues in very low values
    for cnt, rxn in enumerate(model.reactions):
        bounds_temp[cnt] = {
            "rxn_id": rxn.id,
            "lb": rxn.lower_bound,
            "ub": rxn.upper_bound,
        }
    return pd.DataFrame.from_dict(bounds_temp, "index")


# Re-import the MFA data
filename = current_dir + "/TestFile.mat"
simulation_info = pd.read_csv(current_dir + "/experimentalMS_data_I.csv")
simulation_id = "WTEColi_113C80_U13C20_01"
reimport_data = INCA_reimport()
(
    fittedData,
    fittedFluxes,
    fittedFragments,
    fittedMeasuredFluxes,
    fittedMeasuredFragments,
    fittedMeasuredFluxResiduals,
    fittedMeasuredFragmentResiduals,
    simulationParameters,
) = reimport_data.reimport(filename, simulation_info, simulation_id)
# Import the conbra model
model = cobra.io.load_json_model(current_dir + "/iJO1366.json")
unconstraint_bounds = get_bounds_df(model)
# Copy the model in order to re-use it a few times
# Get info about the model and the biomass reactions
model_input = model.copy()
constrained_model = add_constraints(model_input, fittedFluxes)
constrained_bounds = get_bounds_df(constrained_model)
find_biomass_reaction(
    constrained_model, biomass_string=["Biomass", "BIOMASS", "biomass"]
)
min_val = get_min_solution_val(fittedFluxes, biomass_string="Biomass")
adj_fittedFluxes = replace_biomass_rxn_name(
    fittedFluxes,
    biomass_rxn_name="BIOMASS_Ec_iJO1366_core_53p95M",
    biomass_string="Biomass",
)
# Only add the constraints that keep the model in the expected range
model_input = model.copy()
feasible_constrained_model, problems = add_feasible_constraints(
    model_input, adj_fittedFluxes, min_val=min_val,
)
feasible_constrained_bounds = get_bounds_df(feasible_constrained_model)
# Sample and re-format the output
sampled_fluxes = cobra.sampling.sample(model, n=100, processes=2)
fluxes_sampling = reshape_fluxes_escher(sampled_fluxes)
solution = model.optimize()
fluxes_solution = reshape_fluxes_escher(solution)
# Produce relaxation data
infeasible_model = constrained_model.copy()
cons_table = bound_relaxation(
    infeasible_model,
    adj_fittedFluxes,
    destructive=True,
    fluxes_to_ignore=[],
)
relaxed_bounds = get_bounds_df(infeasible_model)

pickle.dump(
    [
        fittedFluxes,
        unconstraint_bounds,
        constrained_bounds,
        min_val,
        adj_fittedFluxes,
        problems,
        feasible_constrained_bounds,
        sampled_fluxes,
        fluxes_sampling,
        solution,
        fluxes_solution,
        cons_table,
        relaxed_bounds,
    ],
    filehandler,
)

filehandler.close()
