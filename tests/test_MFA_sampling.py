import unittest
import pickle
import pathlib
import os
import cobra
import pandas as pd
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

os.chdir(current_dir + "/test_data/MFA_modelInputsData")


class test_methods(unittest.TestCase):

    maxDiff = None

    # Create method to compare dataframes
    def assertDataframeEqual(self, a, b, msg):
        try:
            pd.testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        file_obj = open(
            current_dir
            + "/test_data/MFA_modelInputsData/sampling_test_data.obj",
            "rb",
        )
        (
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
        ) = pickle.load(file_obj)
        file_obj.close()

        self.simulation_info = pd.read_csv(
            current_dir
            + "/test_data/MFA_modelInputsData/experimentalMS_data_I.csv"
        )
        self.simulation_id = "WTEColi_113C80_U13C20_01"
        self.model = cobra.io.load_json_model(
            current_dir + "/test_data/MFA_modelInputsData/iJO1366.json")
        self.constrained_model = add_constraints(
            self.model.copy(), adj_fittedFluxes
        )
        self.fittedFluxes = fittedFluxes
        self.unconstraint_bounds = unconstraint_bounds
        self.constrained_bounds = constrained_bounds
        self.min_val = min_val
        self.adj_fittedFluxes = adj_fittedFluxes
        self.problems = problems
        self.feasible_constrained_bounds = feasible_constrained_bounds
        self.sampled_fluxes = sampled_fluxes
        self.fluxes_sampling = fluxes_sampling
        self.solution = solution
        self.fluxes_solution = fluxes_solution
        self.cons_table = cons_table
        self.relaxed_bounds = relaxed_bounds

        # Add the method to compare dataframes in the class
        self.addTypeEqualityFunc(pd.DataFrame, self.assertDataframeEqual)

    @staticmethod
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

    def test_add_constraints(self):
        unconstraint_bounds = self.unconstraint_bounds
        constrained_bounds = self.constrained_bounds
        constrained_model = add_constraints(
            self.model.copy(),
            self.fittedFluxes,
        )
        constrained_bounds_ = self.get_bounds_df(constrained_model)
        self.assertFalse(unconstraint_bounds.equals(constrained_bounds_))
        self.assertEqual(constrained_bounds, constrained_bounds_)

    def test_find_biomass_reaction(self):
        biomass_reaction_ids = find_biomass_reaction(
            self.constrained_model,
            biomass_string=["Biomass", "BIOMASS", "biomass"],
        )
        # This one basically just checks if there is an output
        self.assertIsInstance(biomass_reaction_ids, list)
        # This one makes sure that the output list contains a reaction name
        self.assertIsInstance(biomass_reaction_ids[0], str)

    def test_get_min_solution_val(self):
        # Find in fittedFluxes
        min_val = self.min_val
        min_val_ = get_min_solution_val(
            self.fittedFluxes, biomass_string="Biomass"
        )
        self.assertEqual(min_val, min_val_)
        # Do not find in fake example (=0)
        fauxfittedFluxes = self.fittedFluxes
        fauxfittedFluxes.at[11, "rxn_id"] = "Removed_ID"
        no_BM_val = get_min_solution_val(
            fauxfittedFluxes, biomass_string="Biomass"
        )
        self.assertEqual(no_BM_val, 0)

    def test_replace_biomass_rxn_name(self):
        # Replace in fittedFluxes
        adj_fittedFluxes = self.adj_fittedFluxes
        adj_fittedFluxes_ = replace_biomass_rxn_name(
            self.fittedFluxes,
            biomass_rxn_name="BIOMASS_Ec_iJO1366_core_53p95M",
            biomass_string="Biomass",
        )
        self.assertEqual(adj_fittedFluxes, adj_fittedFluxes_)
        # Replace in a fake sample
        test_df = pd.DataFrame({"rxn_id": "Biomass"}, index=[0])
        test_df_replaced = replace_biomass_rxn_name(
            test_df, biomass_string="Biomass", biomass_rxn_name="It works!"
        )
        self.assertEqual(test_df_replaced["rxn_id"][0], "It works!")

    def test_add_feasible_constraints(self):
        problems = self.problems
        unconstraint_bounds = self.unconstraint_bounds
        feasible_constrained_bounds = self.feasible_constrained_bounds
        feasible_constrained_model, problems_ = add_feasible_constraints(
            self.model.copy(),
            self.adj_fittedFluxes,
            min_val=self.min_val,
        )
        feasible_constrained_bounds_ = self.get_bounds_df(
            feasible_constrained_model
        )
        self.assertEqual(problems, problems_)
        self.assertFalse(unconstraint_bounds.equals(
            feasible_constrained_bounds_))
        self.assertEqual(
            feasible_constrained_bounds, feasible_constrained_bounds_
        )

    def test_reshape_fluxes_escher_sampling(self):
        # Test if a samples result has more than one value per reaction
        # coming in and the right shape coming out
        self.assertTrue(
            len(self.sampled_fluxes[self.sampled_fluxes.columns[0]]) > 1
        )
        # Compare to reference
        fluxes_sampling = self.fluxes_sampling
        fluxes_sampling_ = reshape_fluxes_escher(self.sampled_fluxes)
        self.assertEqual(fluxes_sampling, fluxes_sampling_)
        # Test shape of output
        test_list = []
        test_list.append(fluxes_sampling[self.sampled_fluxes.columns[0]])
        self.assertTrue(len(test_list) == 1)

    def test_reshape_fluxes_escher_solution(self):
        # Test if a samples result has only one value per reaction
        # coming in and the right shape coming out
        test_list_input = []
        test_list_input.append(self.solution.fluxes[0])
        self.assertTrue(len(test_list_input) == 1)
        # Compare to reference
        fluxes_solution = self.fluxes_solution
        fluxes_solution_ = reshape_fluxes_escher(self.solution)
        self.assertEqual(fluxes_solution, fluxes_solution_)
        # Test shape of output
        test_list_output = []
        test_list_output.append(fluxes_solution[self.solution.fluxes.index[0]])
        self.assertTrue(len(test_list_output) == 1)

    def test_bound_relaxation(self):
        try:
            # regular test
            cons_table = self.cons_table
            cons_table_ = bound_relaxation(
                self.constrained_model.copy(),
                self.fittedFluxes,
                destructive=True,
                fluxes_to_ignore=[],
            )
            self.assertEqual(cons_table, cons_table_)
        except Exception as exception:
            # Exception if can't find Gurobi
            self.assertIsInstance(exception, ModuleNotFoundError)
            self.assertEqual(str(exception), "Requires Gurobi solver.")


if __name__ == "__main__":
    unittest.main()
