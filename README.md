# Nextflow SQL to Parquet
Nextflow pipeline to convert SQL queries to Parquet files.

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
    }
}
```
Required values:
- data_type
- main_sql: can be raw SQL or a path to a SQL file relative to the current directory

Optional values:
- supplementary_data: dict

For supplementary queries, the first column of each query is used to merge the main query and the supplementary queries together. It is possible to use parameterized queries. With MySQL, parameters in a SQL statement can be positional (`%s`) and given as a tuple or named (`%(name)s`) and given as a dictionary. For example:
```
supplementary_data = {"key1" : """SELECT col FROM table""", 
    "key2" : ["""SELECT col FROM table WHERE condition1 = %s AND condition2 = %s""", ("param1", "param2")],
    "key3" : ["""SELECT col FROM table WHERE condition1 = %(c1)s AND condition2 = %(c2)s""", {"c1" : "param1", "c2" : "param2"}]} 
```

## Run
```
nextflow run main.nf
```