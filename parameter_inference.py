########################################################################################################################
# Module: parameter_inference.py
# Description: Tune hyperparameters using some Porto taxi data.
#
# Web: https://github.com/SamDuffield/bmm
########################################################################################################################

import numpy as np
import matplotlib.pyplot as plt

from bmm.src.data.utils import source_data, read_data, choose_data
from bmm.src.tools.graph import load_graph

import bmm

np.random.seed(0)

# Source data paths
_, process_data_path = source_data()

# Load networkx graph
graph = load_graph()

# Load taxi data
# data_path = choose_data()

# data_path = process_data_path + "/data/portotaxi_06052014_06052014_utm_1730_1745.csv"
# raw_data = read_data(data_path, 100).get_chunk()
# polyline_indices = np.arange(21, 26)

data_path = process_data_path + "/data/portotaxi_05052014_12052014_utm_bbox.csv"
raw_data = read_data(data_path)
# polyline_indices = np.linspace(30, len(raw_data) - 1, 10, dtype=int)
# polyline_indices = np.arange(10) * 3300
polyline_indices = np.array([0,  3300,  6600,  9900, 13200, 16500, 19800, 23101, 26400, 29700])

polylines = [np.asarray(raw_data['POLYLINE_UTM'][single_index]) for single_index in polyline_indices]
lens = [len(po) for po in polylines]
del raw_data

# mm_model = bmm.GammaMapMatchingModel()
mm_model = bmm.LogNormalMapMatchingModel()
# mm_model = bmm.src.inference.model.TweedieMapMatchingModel()

timestamps = 15
n_iter = 100

params_track = bmm.offline_em(graph, mm_model, timestamps, polylines, n_iter=n_iter, max_rejections=0,
                              initial_d_truncate=50)

# mm_model.deviation_beta = 3.3
parts = bmm.offline_map_match(graph, polylines[0], 100, 15, mm_model)

