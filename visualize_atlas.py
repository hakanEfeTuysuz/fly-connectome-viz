import pandas as pd
import plotly.graph_objects as go

neurons = pd.read_csv('atlas_neurons.csv')
edges = pd.read_csv('atlas_edges.csv')

region_colors = {
    'Mushroom Body': 'gold',
    'Ellipsoid Body': 'royalblue',
    'Antennal Lobe': 'seagreen',
    'Medulla (Optic Lobe)': 'crimson',
}

pos = {row['bodyId']: (row['x'], row['y'], row['z']) for _, row in neurons.iterrows()}
valid_ids = set(pos.keys())
edges = edges[edges['bodyId_pre'].isin(valid_ids) & edges['bodyId_post'].isin(valid_ids)]

fig = go.Figure()

edge_x, edge_y, edge_z = [], [], []
for _, row in edges.iterrows():
    x0, y0, z0 = pos[row['bodyId_pre']]
    x1, y1, z1 = pos[row['bodyId_post']]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]
    edge_z += [z0, z1, None]

fig.add_trace(go.Scatter3d(
    x=edge_x, y=edge_y, z=edge_z,
    mode='lines', line=dict(width=1, color='lightgray'),
    hoverinfo='none', showlegend=False
))

for region, group in neurons.groupby('region'):
    fig.add_trace(go.Scatter3d(
        x=group['x'], y=group['y'], z=group['z'],
        mode='markers',
        name=f"{region} — {group['function'].iloc[0]}",
        marker=dict(size=4, color=region_colors.get(region, 'gray')),
        text=[f"Bölge: {region}<br>İşlev: {f}<br>Tip: {t}<br>ID: {b}"
              for f, t, b in zip(group['function'], group['type'], group['bodyId'])],
        hoverinfo='text'
    ))

fig.update_layout(
    title="Drosophila Beyni — İşlevsel Bölge Atlası",
    scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False),
               zaxis=dict(visible=False), aspectmode='data'),
    legend=dict(title="Beyin Bölgeleri")
)
fig.write_html('brain_atlas.html')
import webbrowser
import os

file_path = 'file://' + os.path.realpath('brain_atlas.html')
webbrowser.open(file_path)
print("Tarayıcıda açılıyor...")