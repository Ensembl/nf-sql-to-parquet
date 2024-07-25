# Running the pipeline on codon SLURM
This script was used to generate Parquet files for the 241 genomes in `241_genomes.tsv` with core URI `mysql://anonymous@ensembldb.ensembl.org/` and compara URI `mysql://ensro@mysql-ens-sta-6:4695/` version `110` in July 2024.

## Load modules
Create module if unavailable
```
modenv_team enable production/parquet_e113_mvp  
```

Load modules
```
module load production/parquet_e113_mvp
module load rel_env
```

# Run pipeline

Adjust variables and arguments in `run_parquet.sh` as necessary, or remove them to use the one defined in `nextflow/nextflow.config`. 

`run_parquet.sh` contains the genome UUID for *Homo sapiens*. For the 241 genomes, run `read_241.py` then copy the output in `--genome_uuid` in the `run_parquet.sh` script.

Run pipeline
```
bash run_parquet.sh
```