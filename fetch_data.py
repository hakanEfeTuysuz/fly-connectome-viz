import os
import pandas as pd
from dotenv import load_dotenv
from neuprint import Client, NeuronCriteria as NC, fetch_adjacencies, fetch_neurons

load_dotenv()

client = Client(
    'neuprint.janelia.org',
    dataset='hemibrain:v1.2.1',
    token=os.environ['NEUPRINT_APPLICATION_CREDENTIALS']
)

criteria = NC(rois=['EB'], status='Traced')

neuron_info, neurons_edges = fetch_adjacencies(criteria, criteria)

# Gerçek 3D soma (hücre gövdesi) konumlarını çek
soma_df, _ = fetch_neurons(criteria)
soma_df = soma_df[['bodyId', 'somaLocation']].dropna(subset=['somaLocation'])
soma_df[['x', 'y', 'z']] = pd.DataFrame(soma_df['somaLocation'].tolist(), index=soma_df.index)
soma_df = soma_df.drop(columns=['somaLocation'])

neuron_info = neuron_info.merge(soma_df, on='bodyId', how='left')

neuron_info.to_csv('neurons.csv', index=False)
neurons_edges.to_csv('edges.csv', index=False)
print(f"{len(neuron_info)} nöron, {len(neurons_edges)} bağlantı kaydedildi.")
print(f"{neuron_info['x'].notna().sum()} nöronun gerçek konum bilgisi var.")