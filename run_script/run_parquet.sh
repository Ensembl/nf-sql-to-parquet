#!/bin/bash


WORK_LOCATION=/hps/nobackup/flicek/ensembl/production/nextflow/sukanya_parquet_files
export NXF_WORK=${WORK_LOCATION}
PROFILE=slurm

mkdir -p ${WORK_LOCATION}
mkdir -p ${WORK_LOCATION}/work
cd $WORK_LOCATION

export BASE_DIR=/hps/software/users/ensembl/production/vinay/modenv/production/vinay_mvp
#export NF_PY_SCRIPTS_PATH="/hps/software/users/ensembl/repositories/vinay/develop/ensembl-production/nextflow/nf-py-scripts/"
export METADATA_DB_URI=`mysql-ens-test-1-ensadmin details url`ensembl_genome_metadata
export TAXONOMY_DB_URI=`mysql-ens-test-1-ensadmin details url`ensembl_genome_metadata

#core db info
export CORE_DB_HOST_URI="mysql://anonymous@ensembldb.ensembl.org/"

#dataset details
export DATASET_TYPE="genebuild"
export DATASET_STATUS="Released"
export UPDATE_DATASET_STATUS="Released"
export BATCH_SIZE=0

#a7335667-93e7-11ec-a39d-005056b38ce3 homo_sapiens

nextflow run /homes/sukanya/nf-sql-to-parquet/nextflow/main.nf \
	-c /homes/sukanya/nf-sql-to-parquet/nextflow/nextflow.config \
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
	--genome_uuid a7335667-93e7-11ec-a39d-005056b38ce3 \
        --output_dir /hps/nobackup/flicek/ensembl/production/nextflow/sukanya_parquet_files/parquet_output \
        --target_dir 241_genomes \
        -resume
