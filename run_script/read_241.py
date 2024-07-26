import pandas as pd

df = pd.read_csv('241_genomes.tsv', sep='\t')
li = df['genome_uuid'].tolist()
uuids = str(li).replace("'", "").replace("[" , "").replace("]", "").replace(" ", "")

print(uuids)
