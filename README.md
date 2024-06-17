# Nextflow SQL to Parquet
SQL query to Parquet files.

## Pipeline configuration
Configure parameters in `nextflow.config` or specify them on the command line (e.g. `--query_dir value`)

### Queries
Each SQL query has a JSON config, following this model:
```json
{
    "data_type": "transcript",
    "main_sql": "queries/create_parquet/transcript.sql",
    "supplementary_data": {
        "miRNA_coordinates": "SELECT transcript_id,value as miRNA_coordinates FROM transcript_attrib WHERE attrib_type_id=15",
        "frameshift": "SELECT transcript_id, value AS frameshift FROM transcript_attrib  WHERE attrib_type_id=59",
        "ncRNA": "SELECT transcript_id, value AS ncRNA FROM transcript_attrib WHERE attrib_type_id=62"
    },
    "lookup_key": ["miRNA_coordinates", "frameshift", "ncRNA"]
}
```
Required values:
- data_type
- main_sql: can be raw SQL or a path to a SQL file relative to the current directory

Optional values:
- supplementary_data: dict
- lookup_key: list

For supplementary queries, the first column of each query is used to merge the main query and the supplementary queries together.

With MySQL, parameters in a SQL statement can be positional (`%s`) and given as a tuple or named (`%(name)s`) and given as a dictionary. For example:
```
supplementary_data = {"key1" : """SELECT col FROM table""", 
    "key2" : ["""SELECT col FROM table WHERE condition1 = %s AND condition2 = %s""", ("param1", "param2")],
    "key3" : ["""SELECT col FROM table WHERE condition1 = %(c1)s AND condition2 = %(c2)s""", {"c1" : "param1", "c2" : "param2"}]} 
```


### Species
Each species has a JSON config, following this model:
```json
{
    "host": "ensembldb.ensembl.org",
    "port": 3306,
    "user": "anonymous",
    "database": "homo_sapiens_core_111_38",
    "password": "",
    "species_id": 1,
    "production_name": "homo_sapiens"
}
```
Only one of `species_id` or `production_name` is required.


## Run
```
nextflow run main.nf
```