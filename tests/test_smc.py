########################################################################################################################
# Module: tests/test_smc.py
# Description: Tests for SMC implementation.
#
# Web: https://github.com/SamDuffield/bayesian-traffic
########################################################################################################################

import unittest
import os
import json

import pandas as pd
import osmnx as ox
import numpy as np

from bmm.src.tools.edges import graph_edges_gdf
from bmm.src.inference import smc, proposal
from bmm.src.inference.model import ExponentialMapMatchingModel


def read_data(path, nrows=None):
    data_reader = pd.read_csv(path, nrows=10)
    data_columns = data_reader.columns
    polyline_converters = {col_name: json.loads for col_name in data_columns
                           if 'POLYLINE' in col_name}

    return pd.read_csv(path, converters=polyline_converters, nrows=nrows)


def load_test_data(test_data_path=None, nrows=None):
    if test_data_path is None:
        test_dir_path = os.path.dirname(os.path.realpath(__file__))
        test_files = os.listdir(test_dir_path)
        test_data_files = [file_name for file_name in test_files if file_name[:8] == 'testdata']
        if len(test_data_files) == 0:
            assert ValueError("Test data not found")
        test_data_file = test_data_files[0]
        test_data_path = test_dir_path + '/' + test_data_file

    return read_data(test_data_path, nrows)


def load_graph(test_graph_path=None):
    if test_graph_path is None:
        test_dir_path = os.path.dirname(os.path.realpath(__file__))
        test_files = os.listdir(test_dir_path)
        test_graph_files = [file_name for file_name in test_files if file_name[:9] == 'testgraph']
        if len(test_graph_files) == 0:
            assert ValueError("Test graph not found")
        test_graph_file = test_graph_files[0]
        test_graph_path = test_dir_path + '/' + test_graph_file

    return ox.load_graphml(test_graph_path)


class TestWithGraphAndData(unittest.TestCase):
    def setUp(self):
        self.graph = load_graph()
        self.gdf = graph_edges_gdf(self.graph)
        self.test_data = load_test_data(nrows=10)


class TestInitiateParticles(TestWithGraphAndData):
    def test_initiate(self):
        self.particles = smc.initiate_particles(self.graph, self.test_data['POLYLINE_UTM'][0][0], 10)
        self.assertEqual(self.particles.n, 10)
        self.assertEqual(self.particles[0].shape, (1, 8))
        init_arr = np.array(self.particles.particles)[:, 0, :]
        self.assertGreater(np.unique(init_arr[:, 5]).size, 3)
        self.assertEqual(init_arr[:, 0].sum(), 0.)
        self.assertEqual(init_arr[:, -1].sum(), 0.)


class TestProposeParticles(TestWithGraphAndData):
    def test_propose(self):
        self.particles = smc.initiate_particles(self.graph, self.test_data['POLYLINE_UTM'][0][0], 10)
        proposed_particle, weight, prior_norm = proposal.optimal_proposal(self.graph,
                                                                          self.particles[0],
                                                                          self.test_data['POLYLINE_UTM'][0][1],
                                                                          15,
                                                                          ExponentialMapMatchingModel())
        self.assertEqual(proposed_particle.shape[1], 8)
        self.assertIsInstance(weight, float)
        self.assertGreater(weight, 0.)
        self.assertGreaterEqual(proposed_particle.shape[0], 2)
        self.assertEqual(proposed_particle.shape[1], 8)
        self.assertEqual(np.isnan(proposed_particle).sum(), 0)
        self.assertEqual(proposed_particle[:, 0].sum(), 15.)
        self.assertEqual(proposed_particle[-1, 0], 15.)
        self.assertGreaterEqual(proposed_particle[-1, -1], 0.)


class TestUpdateParticlesPF(TestWithGraphAndData):
    def test_update(self):
        self.particles = smc.initiate_particles(self.graph, self.test_data['POLYLINE_UTM'][0][0], 10,
                                                filter_store=False)
        updated_particles = smc.update_particles_flpf(self.graph,
                                                      self.particles,
                                                      self.test_data['POLYLINE_UTM'][0][1],
                                                      15,
                                                      ExponentialMapMatchingModel(),
                                                      proposal.optimal_proposal)
        self.assertEqual(updated_particles.n, 10)
        self.assertEqual(len(updated_particles.particles), 10)
        for proposed_particle in updated_particles:
            self.assertEqual(proposed_particle.shape[1], 8)
            self.assertGreaterEqual(proposed_particle.shape[0], 2)
            self.assertEqual(proposed_particle.shape[1], 8)
            self.assertEqual(np.isnan(proposed_particle).sum(), 0)
            self.assertEqual(proposed_particle[:, 0].sum(), 15.)
            self.assertEqual(proposed_particle[-1, 0], 15.)
            self.assertGreaterEqual(proposed_particle[-1, -1], 0.)
        self.assertGreater(np.unique([pp[-1, 5] for pp in updated_particles]).size, 3)


class TestUpdateParticlesBSi(TestWithGraphAndData):
    def test_update(self):
        self.particles = smc.initiate_particles(self.graph, self.test_data['POLYLINE_UTM'][0][0], 10,
                                                filter_store=True)
        updated_particles = smc.update_particles_flbs(self.graph,
                                                      self.particles,
                                                      self.test_data['POLYLINE_UTM'][0][1],
                                                      15,
                                                      ExponentialMapMatchingModel(),
                                                      proposal.optimal_proposal)
        self.assertEqual(updated_particles.n, 10)
        self.assertEqual(len(updated_particles.particles), 10)
        for proposed_particle in updated_particles:
            self.assertEqual(proposed_particle.shape[1], 8)
            self.assertGreaterEqual(proposed_particle.shape[0], 2)
            self.assertEqual(proposed_particle.shape[1], 8)
            self.assertEqual(np.isnan(proposed_particle).sum(), 0)
            self.assertEqual(proposed_particle[:, 0].sum(), 15.)
            self.assertEqual(proposed_particle[-1, 0], 15.)
            self.assertGreaterEqual(proposed_particle[-1, -1], 0.)
        self.assertGreater(np.unique([pp[-1, 5] for pp in updated_particles]).size, 3)


if __name__ == '__main__':
    unittest.main()
