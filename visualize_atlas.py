import pandas as pd
import plotly.graph_objects as go

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

# Gürültüyü azalt: sadece en güçlü (üst %25) bağlantıları göster
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
    hoverinfo='none', name='Bölgeler arası bağlantı'
))

for region, group in neurons.groupby('region'):
    fig.add_trace(go.Scatter3d(
        x=group['x'], y=group['y'], z=group['z'],
        mode='markers',
        name=f"{region} — {group['function'].iloc[0]}",
        marker=dict(
            size=5,
            color=region_colors.get(region, 'gray'),
            opacity=0.9,
            line=dict(width=0.5, color='white')
        ),
        text=[f"Bölge: {region}<br>İşlev: {f}<br>Tip: {t}<br>ID: {b}"
              for f, t, b in zip(group['function'], group['type'], group['bodyId'])],
        hoverinfo='text'
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
    legend=dict(title="Beyin Bölgeleri", font=dict(color='white'), bgcolor='rgba(0,0,0,0)'),
    font=dict(color='white')
)
fig.write_html('brain_atlas.html')
fig.show()