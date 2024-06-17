import groovy.json.JsonSlurper

def read_json(json) {
    def jsonSlurper = new JsonSlurper()
    def ConfigFile = new File("${json}")
    String ConfigJSON = ConfigFile.text
    def myConfig = jsonSlurper.parseText(ConfigJSON)
    myConfig
}


process GenomeInfo {
    debug "${params.debug}"
    label 'mem4GB'
    tag 'genomeinfo'

    input:
    val genome_uuid
    val species_name
    val organism_group
    val unreleased_genomes
    val dataset_type
    val metadata_uri
    val taxonomy_uri
    val output_json

    output:
    path "$output_json"

  script :
  def metadata_db_uri          =  metadata_uri ? "--metadata_db_uri $metadata_uri" : ''
  def taxonomy_db_uri          =  taxonomy_uri ? "--taxonomy_db_uri $taxonomy_uri" : ''
  def genome_uuid_param        =  genome_uuid.size() > 0 ?  "--genome_uuid ${genome_uuid.join(" ")}" : ''
  def species_name_param       =  species_name.size() > 0 ?  "--species_name ${species_name.join(" ")}" : ''
  def organism_group_param     =  organism_group.size() > 0 ?  "--organism_group ${organism_group.join(" ")}" : ''
  def unreleased_genomes_param =  unreleased_genomes ? "--unreleased_genomes" : ''
  def dataset_type_param       =  dataset_type.size() > 0 ?  "--dataset_name ${dataset_type.join(" ")}" : ''

  """
  ${params.nf_py_script_path}/genome_info.py \
    $metadata_db_uri $taxonomy_db_uri $genome_uuid_param $species_name_param $organism_group_param \
    $unreleased_genomes_param $dataset_type_param -o $output_json
  """
}



