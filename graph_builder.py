import networkx as nx

def build_graph():

    G = nx.Graph()

    edges = [
        ("Aspirin", "Heart Disease"),
        ("Aspirin", "Stroke"),
        ("Metformin", "Diabetes"),
        ("Ibuprofen", "Inflammation"),
        ("Paracetamol", "Fever"),
        ("Amoxicillin", "Infection"),
        ("Doxycycline", "Acne")
    ]

    G.add_edges_from(edges)

    return G


def get_nodes(G):
    return list(G.nodes())