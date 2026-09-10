import os
import pandas as pd
from dotenv import load_dotenv
from neuprint import Client, NeuronCriteria as NC, fetch_neurons, fetch_adjacencies

load_dotenv()

client = Client(
    'neuprint.janelia.org',
    dataset='hemibrain:v1.2.1',
    token=os.environ['NEUPRINT_APPLICATION_CREDENTIALS']
)

# Bölge: (Görünen isim, işlevi)
REGIONS = {
    'MB(R)': ('Mushroom Body', 'Öğrenme ve hafıza'),
    'EB':    ('Ellipsoid Body', 'Uzamsal yönelim / navigasyon'),
    'AL(R)': ('Antennal Lobe', 'Koku algısı'),
    'ME(R)': ('Medulla (Optic Lobe)', 'Görme - ilk işleme'),
}

MAX_PER_REGION = 150  # performans için her bölgeden en fazla bu kadar nöron

all_neurons = []

for roi, (name, function) in REGIONS.items():
    try:
        criteria = NC(rois=[roi], status='Traced', min_pre=50)
        neurons_df, _ = fetch_neurons(criteria)
    except Exception as e:
        print(f"UYARI: '{roi}' çekilemedi ({e}), atlanıyor.")
        continue

    neurons_df = neurons_df.dropna(subset=['somaLocation'])
    if neurons_df.empty:
        print(f"UYARI: '{roi}' bölgesinde konumlu nöron bulunamadı, atlanıyor.")
        continue

    neurons_df['total_syn'] = neurons_df['pre'] + neurons_df['post']
    neurons_df = neurons_df.sort_values('total_syn', ascending=False).head(MAX_PER_REGION)
    neurons_df[['x', 'y', 'z']] = pd.DataFrame(neurons_df['somaLocation'].tolist(), index=neurons_df.index)
    neurons_df['region'] = name
    neurons_df['function'] = function

    all_neurons.append(neurons_df[['bodyId', 'type', 'instance', 'region', 'function', 'x', 'y', 'z']])
    print(f"{name}: {len(neurons_df)} nöron eklendi.")

atlas_neurons = pd.concat(all_neurons, ignore_index=True)
atlas_neurons.to_csv('atlas_neurons.csv', index=False)

body_ids = atlas_neurons['bodyId'].tolist()
_, conn_df = fetch_adjacencies(body_ids, body_ids)
conn_df.to_csv('atlas_edges.csv', index=False)

print(f"\nToplam {len(atlas_neurons)} nöron, {len(conn_df)} bağlantı kaydedildi.")