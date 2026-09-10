import pandas as pd
import networkx as nx
import plotly.graph_objects as go

edges = pd.read_csv('edges.csv')
neurons = pd.read_csv('neurons.csv')

# Sadece gerçek konumu bilinen nöronları kullan
neurons = neurons.dropna(subset=['x', 'y', 'z'])
valid_ids = set(neurons['bodyId'])
edges = edges[edges['bodyId_pre'].isin(valid_ids) & edges['bodyId_post'].isin(valid_ids)]

G = nx.DiGraph()
for _, row in neurons.iterrows():
    G.add_node(row['bodyId'], type=row.get('type', 'unknown'), pos=(row['x'], row['y'], row['z']))

for _, row in edges.iterrows():
    G.add_edge(row['bodyId_pre'], row['bodyId_post'], weight=row['weight'])

pos = nx.get_node_attributes(G, 'pos')

edge_x, edge_y, edge_z = [], [], []
for u, v in G.edges():
    x0, y0, z0 = pos[u]
    x1, y1, z1 = pos[v]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]
    edge_z += [z0, z1, None]

edge_trace = go.Scatter3d(
    x=edge_x, y=edge_y, z=edge_z,
    mode='lines',
    line=dict(width=1, color='gray'),
    hoverinfo='none'
)

node_x = [pos[n][0] for n in G.nodes()]
node_y = [pos[n][1] for n in G.nodes()]
node_z = [pos[n][2] for n in G.nodes()]
node_text = [f"ID: {n}<br>Type: {G.nodes[n]['type']}" for n in G.nodes()]

node_trace = go.Scatter3d(
    x=node_x, y=node_y, z=node_z,
    mode='markers',
    marker=dict(size=4, color=[G.degree(n) for n in G.nodes()], colorscale='Viridis', showscale=True),
    text=node_text,
    hoverinfo='text'
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(
    title="Drosophila Beyni — EB Bölgesi (Gerçek Anatomik Konumlar)",
    showlegend=False,
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data'
    )
)
fig.write_html('connectome_3d_anatomic.html')
fig.show()