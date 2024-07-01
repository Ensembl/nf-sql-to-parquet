#!/usr/bin/env nextflow
import groovy.json.JsonSlurper
nextflow.enable.dsl=2

include {
  GenomeInfo;
} from "${params.ensembl_production_nf_modules}/productionCommon";

include {
  convertToList;
} from "${params.ensembl_production_nf_modules}/utils";




// Parameter default values
params.help = false
println """\
        Parquet File Generation Pipeline
        =================================
        pipeline_dir     =  ${params.pipeline_dir}
        user             =  ${params.user}
        email            =  ${params.email}
        base_dir         =  ${params.base_dir}
        scripts_dir      =  ${params.scripts_dir}
        query_dir        =  ${params.query_dir}
        output_dir       =  ${params.output_dir}
        core_db_host_uri =  ${params.core_db_host_uri}
        metadata_db_uri  =  ${params.metadata_db_uri}
        production_nf_base = ${params.ensembl_production_nf_base}
        nf_py_script_path = ${params.nf_py_script_path}
        #########################################################
        Metadata Params
        #########################################################
        params.genome_uuid           = ${params.genome_uuid}
        params.dataset_uuid          = ${params.dataset_uuid}
        params.organism_group_type   = ${params.organism_group_type}
        params.division              = ${params.division}
        params.dataset_type          = ${params.dataset_type}
        params.species               = ${params.species}
        params.antispecies           = ${params.antispecies}
        params.dataset_status        = ${params.dataset_status}
        params.update_dataset_status = ${params.update_dataset_status}
        params.batch_size            = ${params.batch_size}
        params.page                  = ${params.page}
        params.columns               = ${params.columns}
        params.metadata_db_uri       = ${params.metadata_db_uri}
        """
        .stripIndent()

println("${params.ensembl_production_nf_modules}/productionCommon")


def helpMessage() {
  log.info"""
  Usage:
  nextflow run main.nf <ARGUMENTS>
  TODO: Fill the params for help message
  """.stripIndent()
}

def read_json(json) {
    def jsonSlurper = new JsonSlurper()
    def ConfigFile = new File("${json}")
    String ConfigJSON = ConfigFile.text
    def myConfig = jsonSlurper.parseText(ConfigJSON)
    myConfig
}


process SqlToParquet {
    label 'mem2GB'
    publishDir "${params.output_dir}", mode: 'copy'
    
    tag {"$production_name - $query"}

    input:
    tuple(val(genome_uuid), val(production_name), val(database))
    each query

    output:
    path "**.parquet"

    script:
    // get SQL script absolute path
    def query_config = read_json("${query}")
    if ( "${query_config.main_sql}".split("\\.")[-1] == "sql" ){
        sql = "${params.scripts_dir}/${query_config.main_sql}"
    } else {
        sql = "${query_config.main_sql}"
    }
    
    """
    ${params.scripts_dir}/main.py --query_config $query --main_query $sql -o ${params.target_dir} --genome_uuid $genome_uuid --production_name $production_name --core_uri ${params.core_db_host_uri} --database $database
    """
}

workflow {

    def jsonSlurper       = new groovy.json.JsonSlurper()
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
    output_json           = 'genome_info.json'

    GenomeInfo( metadata_db_uri, genome_uuid, dataset_uuid,
                organism_group_type, division, dataset_type,
                species, antispecies, dataset_status, update_dataset_status,
                batch_size, page, columns, output_json
    )

    genomes_ch = GenomeInfo.out[0].splitText().map {
                    genome_json = jsonSlurper.parseText(it.replaceAll('\n', ''))
                    return [genome_json['genome_uuid'], genome_json['species'], genome_json['database_name']]
                }.map { it }

   queries_ch = Channel.fromPath("${params.query_dir}/*.json", checkIfExists: true)
   SqlToParquet(genomes_ch, queries_ch)
}