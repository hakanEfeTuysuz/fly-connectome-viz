import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

neurons = pd.read_csv('atlas_neurons.csv')
edges = pd.read_csv('atlas_edges.csv')

region_colors = {
    'Mushroom Body': '#FFD700',
    'Ellipsoid Body': '#4169E1',
    'Antennal Lobe': '#2ECC71',
    'Medulla (Optic Lobe)': '#FF3B5C',
}

pos = {row['bodyId']: (row['x'], row['y'], row['z']) for _, row in neurons.iterrows()}
region_of = {row['bodyId']: row['region'] for _, row in neurons.iterrows()}
valid_ids = set(pos.keys())

edges = edges[edges['bodyId_pre'].isin(valid_ids) & edges['bodyId_post'].isin(valid_ids)]
threshold = edges['weight'].quantile(0.75)
edges = edges[edges['weight'] >= threshold]

fig = go.Figure()

intra_x, intra_y, intra_z = [], [], []
inter_x, inter_y, inter_z = [], [], []

for _, row in edges.iterrows():
    x0, y0, z0 = pos[row['bodyId_pre']]
    x1, y1, z1 = pos[row['bodyId_post']]
    if region_of[row['bodyId_pre']] == region_of[row['bodyId_post']]:
        intra_x += [x0, x1, None]; intra_y += [y0, y1, None]; intra_z += [z0, z1, None]
    else:
        inter_x += [x0, x1, None]; inter_y += [y0, y1, None]; inter_z += [z0, z1, None]

fig.add_trace(go.Scatter3d(
    x=intra_x, y=intra_y, z=intra_z,
    mode='lines', line=dict(width=1, color='rgba(180,180,180,0.12)'),
    hoverinfo='none', showlegend=False
))

fig.add_trace(go.Scatter3d(
    x=inter_x, y=inter_y, z=inter_z,
    mode='lines', line=dict(width=1.5, color='rgba(255,255,255,0.35)'),
    hoverinfo='none', showlegend=False
))

for region, group in neurons.groupby('region'):
    fig.add_trace(go.Scatter3d(
        x=group['x'], y=group['y'], z=group['z'],
        mode='markers',
        name=region,
        marker=dict(
            size=5,
            color=region_colors.get(region, 'gray'),
            opacity=0.9,
            line=dict(width=0.5, color='white')
        ),
        hoverinfo='skip'
    ))

fig.update_layout(
    title=dict(text="Drosophila Beyni — İşlevsel Bölge Atlası", font=dict(color='white')),
    paper_bgcolor='#0d1117',
    scene=dict(
        xaxis=dict(visible=False, backgroundcolor='#0d1117'),
        yaxis=dict(visible=False, backgroundcolor='#0d1117'),
        zaxis=dict(visible=False, backgroundcolor='#0d1117'),
        bgcolor='#0d1117',
        aspectmode='data'
    ),
    showlegend=True,
    legend=dict(font=dict(color='white'), bgcolor='rgba(0,0,0,0)'),
    font=dict(color='white'),
    width=800, height=600
)

os.makedirs('frames', exist_ok=True)

N_FRAMES = 36
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
    duration=80,
    loop=0
)
print("demo.gif oluşturuldu!")