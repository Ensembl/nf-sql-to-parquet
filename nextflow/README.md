### 1. Setup modenv for codon cluster user

```
ssh codon-login
mkdir -p $HOME/lib
git clone <use_https_or_shh*>Ensembl/ensembl-mod-env.git $HOME/lib/ensembl-mod-env
source $HOME/lib/ensembl-mod-env/install.sh production

#production config yaml are in different repo 

cd ~/lib/
git clone git@gitlab.ebi.ac.uk:ensembl-production/ensembl-prod-env.git
cd ~/lib/
~/lib/ensembl-prod-env/install.sh
```

### 2. Create modenv environment to run parquet nf pipeline

```
ssh codon-login
modenv_create -b 113 -f main production/mvp parquet
#above command create a new venv name `parquet` and clone the required repos and modules in production namespace
```

### 3. Run Nextflow Parquet Pipeline For homo_sapiens
```commandline

module load production/parquet 

cd /hps/nobackup/flicek/ensembl/production/nextflow/parquet_files

WORK_LOCATION=/hps/nobackup/flicek/ensembl/production/nextflow/parquet_files
export NXF_WORK=${WORK_LOCATION}
PROFILE=slurm

mkdir -p ${WORK_LOCATION}
mkdir -p ${WORK_LOCATION}/work
cd $WORK_LOCATION

export METADATA_DB_URI=`mysql-ens-test-1-ensadmin details url`ensembl_genome_metadata
export TAXONOMY_DB_URI=`mysql-ens-test-1-ensadmin details url`ensembl_genome_metadata

#core db info
export CORE_DB_HOST_URI=`st6 details url`

#dataset details
export DATASET_TYPE="genebuild"
export DATASET_STATUS="Released"
export UPDATE_DATASET_STATUS="Released"
export BATCH_SIZE=0

#a7335667-93e7-11ec-a39d-005056b38ce3 homo_sapiens

nextflow run ${BASE_DIR}/nf-sql-to-parquet/nextflow/main.nf \
        -c ${BASE_DIR}/nf-sql-to-parquet/nextflow/nextflow.config \
        -profile $PROFILE \
        -w ${WORK_LOCATION}/work \
        -with-trace ${WORK_LOCATION}/trace.txt \
        -with-report ${WORK_LOCATION}/parquet_report.html \
        --metadata_db_uri $METADATA_DB_URI \
        --taxonomy_db_dbname $TAXONOMY_DB_URI \
        --core_db_host_uri $CORE_DB_HOST_URI \
        --dataset_type $DATASET_TYPE \
        --dataset_status $DATASET_STATUS \
        --batch_size $BATCH_SIZE \
        --update_dataset_status $UPDATE_DATASET_STATUS \
        --genome_uuid a7335667-93e7-11ec-a39d-005056b38ce3
```