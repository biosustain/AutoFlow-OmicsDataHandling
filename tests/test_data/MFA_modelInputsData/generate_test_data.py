# generate test_data
# Last date : 16.12.2020
# By : Matthias Mattanovich (matmat@biosustain.dtu.dk)
# This script is intended to generate sample data and save them into the
# test_data file. The saved objects will then be used to test the
# INCA_script_generator using unit testing.
import pickle
import pandas as pd
from AutoFlow_OmicsDataHandling.INCA_script_generator import (
    limit_to_one_model,
    limit_to_one_experiment,
    # prepare_input,
    initiate_MATLAB_script,
    # reaction_mapping,
    add_reactions_to_script,
    initialize_model,
    symmetrical_metabolites,
    unbalanced_reactions,
    add_reaction_parameters,
    verify_and_estimate,
    add_experimental_parameters,
    mapping,
    script_generator,
    # save_INCA_script,
    runner_script_generator,
    # save_runner_script,
    # run_INCA_in_MATLAB,
)


pd.set_option("mode.chained_assignment", None)
# Use pickle to save python variables
filehandler = open("test_data.obj", "wb")

# measured fragments/MS data, tracers and measured fluxes should be limited to
# one experiment

atomMappingReactions_data_I = pd.read_csv(
    "data_stage02_isotopomer_atomMappingReactions2.csv"
)
modelReaction_data_I = pd.read_csv(
    "data_stage02_isotopomer_modelReactions.csv"
)
biomass_function = "0.176*phe_DASH_L_c + 0.443*mlthf_c + 0.34*oaa_c + 0.326*lys_DASH_L_c + 33.247*atp_c + 0.205*ser_DASH_L_c + 0.129*g3p_c + 0.131*tyr_DASH_L_c + 0.051*pep_c + 0.146*met_DASH_L_c + 0.205*g6p_c + 0.087*akg_c + 0.25*glu_DASH_L_c + 0.25*gln_DASH_L_c + 0.754*r5p_c + 0.071*f6p_c + 0.083*pyr_c + 0.582*gly_c + 0.241*thr_DASH_L_c + 0.229*asp_DASH_L_c + 5.363*nadph_c + 0.087*cys_DASH_L_c + 0.619*3pg_c + 0.402*val_DASH_L_c + 0.488*ala_DASH_L_c + 0.276*ile_DASH_L_c + 0.229*asn_DASH_L_c + 0.09*his_DASH_L_c + 0.428*leu_DASH_L_c + 2.51*accoa_c + 0.281*arg_DASH_L_c + 0.21*pro_DASH_L_c + 0.054*trp_DASH_L_c -> 1.455*nadh_c + 39.68*Biomass_c"  # noqa E501
atomMappingMetabolite_data_I = pd.read_csv(
    "data_stage02_isotopomer_atomMappingMetabolites.csv"
)
measuredFluxes_data_I = pd.read_csv(
    "data_stage02_isotopomer_measuredFluxes.csv"
)
experimentalMS_data_I = pd.read_csv("data-1604345289079.csv")
tracer_I = pd.read_csv("data_stage02_isotopomer_tracers.csv")

# The files need to be limited by model id and mapping id, I picked
# "ecoli_RL2013_02" here
atomMappingReactions_data_I = limit_to_one_model(
    atomMappingReactions_data_I, "mapping_id", "ecoli_RL2013_02"
)
modelReaction_data_I = limit_to_one_model(
    modelReaction_data_I, "model_id", "ecoli_RL2013_02"
)
atomMappingMetabolite_data_I = limit_to_one_model(
    atomMappingMetabolite_data_I, "mapping_id", "ecoli_RL2013_02"
)
measuredFluxes_data_I = limit_to_one_model(
    measuredFluxes_data_I, "model_id", "ecoli_RL2013_02"
)

# Limiting fluxes, fragments and tracers to one experiment
measuredFluxes_data_I = limit_to_one_experiment(
    measuredFluxes_data_I, "experiment_id", "WTEColi_113C80_U13C20_01"
)
experimentalMS_data_I = limit_to_one_experiment(
    experimentalMS_data_I, "experiment_id", "WTEColi_113C80_U13C20_01"
)
tracer_I = limit_to_one_experiment(
    tracer_I, "experiment_id", "WTEColi_113C80_U13C20_01"
)

# Generate variables to save

initiated_MATLAB_script = initiate_MATLAB_script()
# the following function depends on prepare_input() and reaction_mapping()
model_reactions, model_rxn_ids = add_reactions_to_script(
    modelReaction_data_I, atomMappingReactions_data_I, biomass_function
)

initialized_model = initialize_model()

symmetrical_metabolites_script = symmetrical_metabolites(
    atomMappingMetabolite_data_I
)

# this one does not have an output in this set up, change for future version
unbalanced_reactions_script = unbalanced_reactions(
    atomMappingMetabolite_data_I,
)

reaction_parameters = add_reaction_parameters(
    modelReaction_data_I,
    measuredFluxes_data_I,
    model_rxn_ids,
    fluxes_present=True,
)

verify_and_estimate_script = verify_and_estimate()

experimental_parameters, fragments_used = add_experimental_parameters(
    experimentalMS_data_I,
    tracer_I,
    measuredFluxes_data_I,
    atomMappingMetabolite_data_I,
)

mapping_script = mapping(experimentalMS_data_I, fragments_used)

# save_INCA_script(script, scriptname) don't know how to test that
# save_runner_script(runner, scriptname) SAME HERE

# run_INCA_in_MATLAB(INCA_base_directory, script_folder, matlab_script,
# runner_script) can't run MATLAB through CircleCI

script = script_generator(
    modelReaction_data_I,
    atomMappingReactions_data_I,
    biomass_function,
    atomMappingMetabolite_data_I,
    measuredFluxes_data_I,
    experimentalMS_data_I,
    tracer_I,
)
runner = runner_script_generator("TestFile", n_estimates=10)

pickle.dump(
    [
        modelReaction_data_I,
        atomMappingReactions_data_I,
        biomass_function,
        atomMappingMetabolite_data_I,
        measuredFluxes_data_I,
        experimentalMS_data_I,
        tracer_I,
        initiated_MATLAB_script,
        model_reactions,
        model_rxn_ids,
        initialized_model,
        symmetrical_metabolites_script,
        unbalanced_reactions_script,
        reaction_parameters,
        verify_and_estimate_script,
        experimental_parameters,
        fragments_used,
        mapping_script,
        script,
        runner,
    ],
    filehandler,
)

filehandler.close()
