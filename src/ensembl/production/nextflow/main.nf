#!/usr/bin/env nextflow

nextflow.enable.dsl=2

import groovy.json.JsonSlurper

def read_json(json) {
    def jsonSlurper = new JsonSlurper()
    def ConfigFile = new File("${json}")
    String ConfigJSON = ConfigFile.text
    def myConfig = jsonSlurper.parseText(ConfigJSON)
    myConfig
}

process sql_to_parquet {
    errorStrategy 'finish'

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
    queries = Channel.fromPath("${params.query_dir}/*.json", checkIfExists: true)
    species = Channel.fromPath("${params.species_dir}/*.json", checkIfExists: true)

    sql_to_parquet(species, queries)
}