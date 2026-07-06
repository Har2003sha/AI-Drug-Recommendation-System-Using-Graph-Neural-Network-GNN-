import torch
import numpy as np

class GNNPredictor:

    def __init__(self, model, nodes):

        self.model = model
        self.nodes = nodes

        self.node_index = {n:i for i,n in enumerate(nodes)}

    def predict(self, drug, disease):

        if drug not in self.node_index or disease not in self.node_index:
            return "Unknown Pair", 60

        # fake embedding similarity (simplified GNN output)
        score = np.random.randint(70, 99)

        if score > 85:
            return "Strong Repurposing Candidate", score
        elif score > 75:
            return "Moderate Candidate", score
        else:
            return "Weak Candidate", score