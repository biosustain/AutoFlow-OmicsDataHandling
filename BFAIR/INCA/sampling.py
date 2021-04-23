import pandas as pd
import time
import cobra
import re
import functools
import copy
from cobra.exceptions import Infeasible
try:
    from gurobipy import Model as GRBModel
except ModuleNotFoundError:
    pass


def timer(func):
    """
    Wrapper that reports how it took to execute a function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("--- start ---")
        start_time = time.time()
        output = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        min_, sec = divmod(round(elapsed_time), 60)
        hour, min_ = divmod(min_, 60)
        print(f"{func.__name__} takes {hour}h: {min_}min: {sec}sec to run")
        print("--- end ---")
        return output

    return wrapper


def _reshape_fluxes(fittedFluxes):
    """
    Reshaped the flux information from a dataframe to a dict to be used in
    constraint assigning functions.
    """
    MFA_flux_bounds = {}
    for i, rxn in fittedFluxes.iterrows():
        MFA_flux_bounds[rxn["rxn_id"]] = [rxn["flux_ub"], rxn["flux_lb"]]
    return MFA_flux_bounds


def _adjust_bounds(model, rxn, bounds):
    """
    Applied new bounds to specified reactions in a cobra model.
    """
    skip = False
    if bounds[0] < bounds[1]:  # to fix the issue with negaive values above
        try:
            model.reactions.get_by_id(rxn).lower_bound = round(bounds[0], 1)
            model.reactions.get_by_id(rxn).upper_bound = round(bounds[1], 1)
        except KeyError:
            # print(f'Did not work for {rxn}')
            skip = True
    else:
        try:
            model.reactions.get_by_id(rxn).upper_bound = round(bounds[0], 1)
            model.reactions.get_by_id(rxn).lower_bound = round(bounds[1], 1)
        except KeyError:
            # print(f'Did not work for', rxn)
            skip = True
    return model, skip


def _restart_message(restart_counter):
    """
    Prints a message if `add_feasible_constraints()` had to restart.
    """
    extra_minus = "-" * len(str(restart_counter))
    print(f"--------------------------{extra_minus}")
    print(f"Total number of restarts: {restart_counter}")


@timer
def add_constraints(model_input, fittedFluxes):
    """
    Adds all the constraints defined in the input to a
    metabolic model.

    Parameters
    ----------
    model_input : cobra.Model
        Metabolic model.
    fittedFluxes : pandas.DataFrame
        Dataframe (reimported output of an INCA simulation)
        that contains the confidence intervals predicted for
        the model.

    Returns
    -------
    model : cobra.Model
        Metabolic model with adjusted constraints.
    """
    MFA_fluxes = _reshape_fluxes(fittedFluxes)
    model = model_input.copy()
    for rxn, bounds in MFA_fluxes.items():
        model, skip = _adjust_bounds(model, rxn, bounds)
    return model


def find_biomass_reaction(
    model, biomass_string=["Biomass", "BIOMASS", "biomass"]
):
    """
    Identifies the biomass reaction(s) in a metaboli model.

    Parameters
    ----------
    model : cobra.Model
        Metabolic model.
    biomass_string : str or list
        String denoting at least a part of the name of the
        biomass function of the metabolic model or a list
        containing multiple possibilities to be tested.
        Preset to `["Biomass", "BIOMASS", "biomass"]`.

    Returns
    -------
    biomass_reaction_ids : list
        Reaction(s) containing the input string.
    """
    if isinstance(biomass_string, list):
        biomass = biomass_string
    else:
        biomass = list(biomass_string)
    biomass_reaction_ids = []
    for reaction in model.reactions:
        for biomass_spelling in biomass:
            if biomass_spelling in reaction.id:
                biomass_reaction_ids.append(reaction.id)
    return biomass_reaction_ids


def get_min_solution_val(fittedFluxes, biomass_string="Biomass"):
    """
    Finds the value calculated for the biomass function in the
    MFA simulation. This value can be seen as the minimum predicted
    growth rate in subsequent simulations.

    Parameters
    ----------
    fittedFluxes : pandas.DataFrame
        Dataframe (reimported output of an INCA simulation)
        that contains the confidence intervals predicted for
        the model.
    biomass_string : str
        String denoting at least a part of the name of the
        biomass function in the `fittedFluxes` DataFrame.
        Preset to `"Biomass"`.

    Returns
    -------
    min_val : float
        Value calculated for the biomass function in the INCA
        simulation.
    """
    min_val = 0
    for cnt, name in enumerate(fittedFluxes["rxn_id"]):
        if biomass_string in name:
            min_val = fittedFluxes.at[cnt, "flux"]
    return min_val


def replace_biomass_rxn_name(
    fittedFluxes,
    biomass_rxn_name,
    biomass_string="Biomass",
):
    """
    Replaces the biomass function name in the INCA simulation results
    with the biomass funciton name in the metabolic model. This is
    only relevent if a different model was used as a basis for the
    MFA simulation.

    Parameters
    ----------
    fittedFluxes : pandas.DataFrame
        Dataframe (reimported output of an INCA simulation)
        that contains the confidence intervals predicted for
        the model.
    biomass_rxn_name : str
        Name of the biomass reaction in the metabolic model;
        the name that should be assigned to the biomass function in
        `fittedFluxes`.
    biomass_string : str
        String denoting at least a part of the name of the
        biomass function in the `fittedFluxes` dataframe.
        Preset to `"Biomass"`.

    Returns
    -------
    fittedFluxes : pandas.DataFrame
        Dataframe (reimported output of an INCA simulation)
        that contains the confidence intervals predicted for
        the model. Now with same the biomass function name as in
        the metabolic model.
    """
    fittedFluxes_out = copy.deepcopy(fittedFluxes)
    for cnt, name in enumerate(fittedFluxes_out["rxn_id"]):
        if biomass_string in name:
            fittedFluxes_out.at[cnt, "rxn_id"] = biomass_rxn_name
    return fittedFluxes_out


@timer
def add_feasible_constraints(model_input, fittedFluxes, min_val=0):
    """
    Adds contraints to a metabolic model one by one; always checking
    that is still produces a feasible solution and that the predicted
    objective does not fall below a predefined value. If that were to
    happen, the function would restart but skip the reaction that
    caused the issue in the next iteration.

    Parameters
    ----------
    model_input : cobra.Model
        Metabolic model.
    fittedFluxes : pandas.DataFrame
        Dataframe (reimported output of an INCA simulation)
        that contains the confidence intervals predicted for
        the model.
    min_val : float
        Minimum allowed value for the optimized solution predicted for
        the objective. Preset to `0`.

    Returns
    -------
    model : cobra.Model
        Feasible metabolic model with added constraints.
    problems : list
        list of the reaction names of the reactions whose added
        constraints caused the model to fail the tests
        (feasibilty or minimum value).
    """
    no_restart = False
    problems = []
    restart_counter = 0
    MFA_fluxes = _reshape_fluxes(fittedFluxes)
    while no_restart is False:
        model = model_input.copy()
        for rxn, bounds in MFA_fluxes.items():
            if rxn in problems:
                continue
            model, skip = _adjust_bounds(model, rxn, bounds)
            if skip:
                continue
            solution_after_adj = model.optimize()
            if (
                solution_after_adj.objective_value is not None
                and solution_after_adj.objective_value >= min_val
            ):
                no_restart = True
            else:
                print(f"Solution infeasible if adding {rxn}")
                problems.append(rxn)
                no_restart = False
                restart_counter += 1
                break
    _restart_message(restart_counter)
    return model, problems


def reshape_fluxes_escher(sampled_fluxes):
    """
    Reshapes either a cobra solution object or a pandas
    Dataframe containing the sampled fluxes for a metabolic model
    so that they can be visualized in Escher. If a dataframe is
    provided, the mean of all the predictions from each reactions
    will be calculated.

    Parameters
    ----------
    sampled_fluxes : pandas.DataFrame or cobra.Solution
        Object containing reaction fluxes.

    Returns
    -------
    fluxes_escher : dict
        Input for Escher.

    Raises
    ------
    TypeError
        If the wrong type of input was provided.
    """
    fluxes_escher = {}
    if type(sampled_fluxes) is pd.core.frame.DataFrame:
        for col in sampled_fluxes.columns:
            fluxes_escher[col] = sampled_fluxes[col].mean()
    elif type(sampled_fluxes) is cobra.core.solution.Solution:
        reactions = list(sampled_fluxes.fluxes.index)
        for cnt, row in enumerate(sampled_fluxes.fluxes):
            fluxes_escher[reactions[cnt]] = row
    else:
        raise TypeError(
            f"The input is a '{type(sampled_fluxes)}', this type of object"
            " cannot be used here"
        )
    return fluxes_escher


def _extract_bound_violations(
    grb_model, variables, negative_slack_prefix, positive_slack_prefix
):
    """
    Extracts the lower and upper bound changes that have to applied to
    the input model in order ot make the predition feasible.
    """
    # Extracts the magnitude of the bound violations on the relaxed
    # Gurobi model
    epsilon = grb_model.Params.FeasibilityTol
    violations = []
    for var in variables:
        lb_change = -grb_model.getVarByName(negative_slack_prefix + var).X
        ub_change = grb_model.getVarByName(positive_slack_prefix + var).X
        if lb_change < -epsilon:
            violations.append((var, lb_change - epsilon, 0))
        elif ub_change > epsilon:
            violations.append((var, 0, ub_change + epsilon))
    return violations


@timer
def bound_relaxation(
    infeasible_model, fittedFluxes, destructive=True, fluxes_to_ignore=[]
):
    """
    Relaxation function for cobra metabolic models. By making use of the
    Gurobi solver, this functions figures out which bounds have to be
    relaxed by how much in order to make the model solution feasible.
    If `destructive=True`, then these changes are automatically applied.

    Parameters
    ----------
    infeasible_model : cobra.Model
        A metabolic model with constraints that lead to an infeasible
        solution.
    fittedFluxes : pandas.DataFrame
        Dataframe (reimported output of an INCA simulation)
        that contains the confidence intervals predicted for
        the model.
    destructive : bool
        Preset to `True`. If True, then the calculated fluxes will be
        applied to the model.
    fluxes_to_ignore : list
        A list of fluxes that should not be relaxed. Preset to `[]`.

    Returns
    -------
    cons_table : pandas.DataFrame
        A dataframe listing the reactions that have to be relaxed and
        the changes that need to be applied.

    Raises
    ------
    ModuleNotFoundError
        If Gurobi is not the solver of the input model.
    Infeasible
        If the feasibility relaxation fails.
    """
    model = infeasible_model
    if model.solver.interface.__name__ != "optlang.gurobi_interface":
        raise ModuleNotFoundError("Requires Gurobi solver.")

    # copy Gurobi model
    grb_model: GRBModel = model.solver.problem.copy()
    MFA_fluxes = _reshape_fluxes(fittedFluxes)
    reactions_to_relax = list(MFA_fluxes.keys())

    # remove fluxes to ignore
    if fluxes_to_ignore:
        for flux_to_ignore in fluxes_to_ignore:
            reactions_to_relax.remove(flux_to_ignore)

    # There are no metabolites to relax to we leave relax_cons empty
    relax_cons = []

    # Get forward and reverse reaction separately
    relax_vars = [
        grb_model.getVarByName(con.id)
        for con in model.reactions
        if con.id in reactions_to_relax
    ]
    relax_vars_reverse = [
        grb_model.getVarByName(con.reverse_id)
        for con in model.reactions
        if con.id in reactions_to_relax
    ]

    # Combine the lists
    relax_vars = relax_vars + relax_vars_reverse

    cons_penalties = relax_cons
    vars_penalties = [1] * len(relax_vars)

    # perform relaxation of variable bounds
    relax_obj = grb_model.feasRelax(
        relaxobjtype=0,
        minrelax=True,
        vars=relax_vars,
        lbpen=vars_penalties,
        ubpen=vars_penalties,
        constrs=relax_cons,
        rhspen=cons_penalties,
    )

    # check if relaxation was successful
    if relax_obj <= 0:
        raise Infeasible("Failed to create the feasibility relaxation!")
    grb_model.optimize()

    # transfer/record the lower/upper bound changes to the cobra model
    if relax_vars:
        variables = [var.VarName for var in relax_vars]
        rows = []
        violations = _extract_bound_violations(
            grb_model, variables, "ArtL_", "ArtU_"
        )
        for rxn_id, lb_change, ub_change in violations:
            try:
                subsystem = model.reactions.get_by_id(rxn_id).subsystem
            except KeyError:
                subsystem = model.reactions.get_by_id(
                    re.match(".+?(?=_reverse_)", rxn_id)[0]
                ).subsystem
            rows.append(
                {
                    "reaction": rxn_id,
                    "lb_change": lb_change,
                    "ub_change": ub_change,
                    "subsystem": subsystem,
                }
            )
            if destructive:
                if "_reverse_" in rxn_id:
                    # reverse reactions are only temporary for optimization,
                    # so we have to adjust the corresponding original reaction
                    rxn_id = re.match(".+?(?=_reverse_)", rxn_id)[0]
                    lb_change, ub_change = -ub_change, -lb_change
                lb = model.reactions.get_by_id(rxn_id).lower_bound
                ub = model.reactions.get_by_id(rxn_id).upper_bound
                model.reactions.get_by_id(rxn_id).lower_bound = lb + lb_change
                model.reactions.get_by_id(rxn_id).upper_bound = ub + ub_change

        cons_table = pd.DataFrame.from_records(rows, index="reaction")
    else:
        cons_table = None

    return cons_table
