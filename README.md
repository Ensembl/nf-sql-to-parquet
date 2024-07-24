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
- data_type: will be the name of the parquet files
- main_sql: can be raw SQL or a path to a SQL file relative to the current directory

Optional values:
- supplementary_data: dictionary containing supplementary queries, the key for each query does not matter.

For supplementary queries, the first column of each query is used to merge the main query and the supplementary queries together. It is possible to use parameterized queries. With MySQL, parameters in a SQL statement can be positional (`%s`) and given as a tuple or named (`%(name)s`) and given as a dictionary. For example:
```
supplementary_data = {"key1" : """SELECT col FROM table""", 
    "key2" : ["""SELECT col FROM table WHERE condition1 = %s AND condition2 = %s""", ("param1", "param2")],
    "key3" : ["""SELECT col FROM table WHERE condition1 = %(c1)s AND condition2 = %(c2)s""", {"c1" : "param1", "c2" : "param2"}]} 
```

For each JSON config, add a `<Data_type>Schema` class containing the Pyarrow schema for your output table in `nf-sql-to-parquet/src/ensembl/production/sql_to_parquet/table_schema.py`. This stops Parquet from infering column type as integer when there is no values and allows to partition correctly.

Data retrieved through `supplementary_data` is retrieved as arrays. To adjust to Data Connect, empty values in these columns are empty arrays.

## Run
```
nextflow run main.nf
```

### Outputs
Outputs are partitioned by species and organised this way:
```
parquet_output
	├── gene
	|	├── species=species_1
	|	|   └── gene.parquet
	|	└── species=species_2
    |       └── gene.parquet
	├── transcript
	|	├── species=species_1
	|	|   └── transcript.parquet
	|	└── species=species_2
    |       └── transcript.parquet
    └── translation
		├── species=species_1
		|   └── transcript.parquet
		└── species=species_2
            └── transcript.parquet
```