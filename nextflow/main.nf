#!/usr/bin/env nextflow

include {
GenomeInfo;
} '${prams.ensembl_production_nf_modules}';

// Parameter default values
params.help = false
println """\
        Parquet File Generation Pipeline
        =================================
        pipeline_dir     =  ${param.pipeline_dir}
        user             =  ${param.user}
        email            =  ${param.email}
        base_dir         =  ${param.base_dir}
        scripts_dir      =  ${param.script_dir}
        query_dir        =  ${param.query_dir}
        output_dir       =  ${param.output_dir}
        core_db_host_uri =  ${param.core_db_host_uri}
        metadata_db_uri  =  ${param.metadata_db_uri}
        production_nf_base = ${prams.ensembl_production_nf_base}
        """
        .stripIndent()

def helpMessage() {
  log.info"""
  Usage:
  nextflow run main.nf <ARGUMENTS>
  TODO: Fill the params for help message
  """.stripIndent()
}





process SqlToParquet {
    publishDir "results", mode: 'copy'

    input:
    val species
    each query

    output:
    path "**.parquet"

    script:
    // get SQL script absolute path
    def query_config = read_json("${query}")
    if ( "${query_config.main_sql}".split("\\.")[-1] == "sql" ){
        sql_file = new File("${query_config.main_sql}")
        sql = sql_file.canonicalPath
    } else {
        sql = "${query_config.main_sql}"
    }
    // get species or production name
    def species_config = read_json("${species}")
    def species_id = species_config.containsKey("species_id") ? "-s ${species_config.species_id}" : ""
    def production_name = species_config.containsKey("production_name") ? "-pn ${species_config.production_name}" : ""
    """
    main.py -sc $species -qc $query -q $sql -o ${params.target_dir} $species_id $production_name
    """
}

workflow {

    metadata_db_uri       = params.metadata_db_uri
    update_dataset_status = params.update_dataset_status
    batch_size            = params.batch_size
    page                  = params.page
    dataset_type          = params.dataset_type
    genome_uuid           = convertToList(params.genome_uuid)
    dataset_uuid          = convertToList(params.dataset_uuid)
    organism_group_type   = convertToList(params.organism_group_type)
    division              = convertToList(params.division)
    species               = convertToList(params.species)
    antispecies           = convertToList(params.antispecies)
    dataset_status        = convertToList(params.dataset_status)
    columns               = convertToList(params.columns)
    mongo_db_shard_uri    = ( ! params.mongo_db_shard_uri ||   params.mongo_db_shard_uri=="") ?  helpMessage() : params.mongo_db_shard_uri


    output_json     = 'genome_info.json'
    GenomeInfo( metadata_db_uri, genome_uuid, dataset_uuid,
                organism_group_type, division, dataset_type,
                species, antispecies, dataset_status, update_dataset_status,
                batch_size, page, columns, output_json
    )




    sql_to_parquet(species, queries)
}
