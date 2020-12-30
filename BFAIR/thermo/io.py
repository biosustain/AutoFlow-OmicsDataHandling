"""I/O.

This module hosts functions to load cobra models, create and adjust tFBA-ready models.
"""

import os.path
import logging
from glob import glob

from cobra import Model
from cobra.core.singleton import Singleton
from cobra.io import load_json_model
from pytfa import ThermoModel
from pytfa.io import (
    load_thermoDB,
    read_lexicon,
    read_compartment_data,
    annotate_from_lexicon,
    apply_compartment_data,
)
from pytfa.utils.logger import get_bistream_logger

from BFAIR.thermo import static


class _ModelFactory(metaclass=Singleton):
    def __init__(self):
        self._list = [os.path.basename(path).split(".")[0] for path in glob(_path("*.json"))]

    def __dir__(self):
        return self._list

    def __getattr__(self, item):
        if item in self._list:
            return create_model(item)
        return super().__getattribute__(item)


def _path(filename):
    # Returns the path to a file in the static folder
    return os.path.join(os.path.dirname(static.__file__), filename)


def _silence_pytfa(logger_name):
    # Disables the stream logs produced by the pytfa module, keeps file logs
    logger = get_bistream_logger(logger_name)
    for handler in logger.handlers:
        if not isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.ERROR)


def load_cbm(model_name) -> Model:
    """
    Load a JSON cobra model stored in the static folder.

    Parameters
    ----------
    model_name : str
        The name of the model.

    Returns
    -------
    cobra.Model
        The loaded cobra model.
    """
    return load_json_model(_path(model_name + ".json"))


def load_data(model_name):
    """
    Loads pre-curated model-specific thermodynamic information.

    Parameters
    ----------
    model_name : str
        The name of a model.

    Returns
    -------
    thermo_data : dict
        A thermodynamic database.
    lexicon : pandas.DataFrame
        A dataframe linking metabolite IDs to SEED compound IDs.
    compartment_data : dict
        A dictionary with information about each compartment of the model.
    """
    thermo_data = load_thermoDB(_path("thermo_data.thermodb"))
    lexicon = read_lexicon(_path(os.path.join(model_name, "lexicon.csv")))
    compartment_data = read_compartment_data(_path(os.path.join(model_name, "compartment_data.json")))
    return thermo_data, lexicon, compartment_data


def create_model(model_name, thermo_data=None, lexicon=None, compartment_data=None) -> ThermoModel:
    """
    Creates a tFBA-ready model.

    Parameters
    ----------
    model_name : str
        The name of a model.
    thermo_data : dict, optional
        A thermodynamic database. If specified, ``lexicon`` and ``compartment data`` are required.
    lexicon : pandas.DataFrame, optional
        A dataframe linking metabolite IDs to SEED compound IDs. If specified, ``thermo_data`` and ``compartment_data``
        are required.
    compartment_data : dict, optional
        A dictionary containing information about each compartment of the model. If specified, ``thermo_data`` and
        ``lexicon`` are required.

    Returns
    -------
    pytfa.ThermoModel
        A thermodynamic database.

    Raises
    ------
    ValueError
        If any (but not all) of ``thermo_data``, ``lexicon``, and ``compartment_data`` is None.
    """
    data_is_none = [data is None for data in [thermo_data, lexicon, compartment_data]]
    if all(data_is_none):
        thermo_data, lexicon, compartment_data = load_data(model_name)
    elif any(data_is_none):
        raise ValueError("Not all required data supplied.")

    # due to a bug on pytfa, the logger is created with "None" as name
    _silence_pytfa(f'thermomodel_{None}')
    # however, if the model ends up being copied the correct name will be used, so this logger should be silenced too
    _silence_pytfa(f'thermomodel_{model_name}')

    cmodel = load_cbm(model_name)
    tmodel = ThermoModel(thermo_data, cmodel)
    tmodel.name = model_name

    annotate_from_lexicon(tmodel, lexicon)
    apply_compartment_data(tmodel, compartment_data)

    if tmodel.solver.interface.__name__ == "optlang.gurobi_interface":
        tmodel.solver.problem.Params.NumericFocus = 3
    tmodel.solver.configuration.tolerances.feasibility = 1e-9
    tmodel.solver.configuration.presolve = True

    tmodel.prepare()
    tmodel.convert(verbose=False)

    return tmodel


def adjust_model(tmodel: ThermoModel, rxn_bounds, lc_bounds):
    """
    Adjusts the flux bounds and log concentration of a tFBA-ready model.

    Parameters
    ----------
    tmodel : str
        A cobra model with thermodynamic information.
    rxn_bounds : pandas.DataFrame
        A 3-column table containing reaction IDs and flux bounds. The table must have the following columns: ``id``,
        ``lb``, and ``ub``.
    lc_bounds : pandas.DataFrame
        A 3-column table containing metabolite IDs and log concentration bounds. The table must have the following
        columns: ``id``, ``lb``, and ``ub``.
    """
    # constrain reactions (e.g., growth rate, uptake/secretion rates)
    for rxn_id, lb, ub in zip(rxn_bounds["id"], rxn_bounds["lb"], rxn_bounds["ub"]):
        if tmodel.reactions.has_id(rxn_id):
            tmodel.parent.reactions.get_by_id(rxn_id).bounds = lb, ub
            tmodel.reactions.get_by_id(rxn_id).bounds = lb, ub
    # constrain log concentrations
    for met, lb, ub in zip(lc_bounds["id"], lc_bounds["lb"], lc_bounds["ub"]):
        for compartment in tmodel.compartments:
            met_id = met + "_" + compartment
            if tmodel.log_concentration.has_id(met_id):
                (tmodel.log_concentration.get_by_id(met_id).variable.set_bounds(lb, ub))


models = _ModelFactory()
models.__doc__ = """A factory class to create pre-curated thermodynamics-based metabolic models.

Example
-------
>>> dir(models)
['iJO1366', 'small_ecoli']

>>> tmodel = models.small_ecoli
>>> tmodel.slim_optimize()
0.8109972502600706

This is equivalent to ``create_model("small_ecoli")``.
"""
