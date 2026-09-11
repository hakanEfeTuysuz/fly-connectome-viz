import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

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
        name=region,
        marker=dict(size=4, color=region_colors.get(region, 'gray')),
        hoverinfo='skip'
    ))

fig.update_layout(
    title="Drosophila Beyni — İşlevsel Bölge Atlası",
    scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False),
               zaxis=dict(visible=False), aspectmode='data'),
    showlegend=True,
    width=800, height=600
)

os.makedirs('frames', exist_ok=True)

N_FRAMES = 36     # 360° / 10°'lik adımlar
RADIUS = 1.8

frame_paths = []
for i in range(N_FRAMES):
    angle = 2 * np.pi * i / N_FRAMES
    fig.update_layout(scene_camera=dict(
        eye=dict(x=RADIUS * np.cos(angle), y=RADIUS * np.sin(angle), z=0.8)
    ))
    path = f'frames/frame_{i:03d}.png'
    fig.write_image(path)
    frame_paths.append(path)
    print(f"Kare {i + 1}/{N_FRAMES} oluşturuldu")

images = [Image.open(p) for p in frame_paths]
images[0].save(
    'demo.gif',
    save_all=True,
    append_images=images[1:],
    duration=80,   # her kare 80ms
    loop=0
)
print("demo.gif oluşturuldu!")