import networkx as nx
import matplotlib.pyplot as plt
from graph_builder import build_graph

def visualize():

    G = build_graph()

    plt.figure(figsize=(8,6))

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000)

    plt.title("Drug-Disease Knowledge Graph")
    plt.show()

if __name__ == "__main__":
    visualize()