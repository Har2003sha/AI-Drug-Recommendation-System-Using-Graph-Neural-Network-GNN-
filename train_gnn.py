import torch
import torch.nn as nn
import torch.optim as optim

from graph_builder import build_graph, get_nodes

# Simple embedding-based GCN-like model
class SimpleGCN(nn.Module):

    def __init__(self, n_nodes, emb_dim=16):
        super(SimpleGCN, self).__init__()

        self.embedding = nn.Embedding(n_nodes, emb_dim)
        self.fc = nn.Linear(emb_dim, 1)

    def forward(self, x):
        x = self.embedding(x)
        x = torch.relu(x)
        x = self.fc(x)
        return torch.sigmoid(x)


# Fake training data (drug-disease pairs)
data = [
    (0,1,1),(0,2,1),(1,3,1),
    (2,4,1),(3,5,1),(4,6,1)
]

def train():

    G = build_graph()
    nodes = get_nodes(G)

    node_to_idx = {n:i for i,n in enumerate(nodes)}

    model = SimpleGCN(len(nodes))
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    for epoch in range(50):

        total_loss = 0

        for d, dis, label in data:

            x = torch.tensor([d], dtype=torch.long)

            pred = model(x)
            loss = criterion(pred, torch.tensor([[label]], dtype=torch.float))

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch} Loss: {total_loss:.4f}")

    torch.save(model.state_dict(), "gnn_model.pt")
    print("Model saved!")

if __name__ == "__main__":
    train()