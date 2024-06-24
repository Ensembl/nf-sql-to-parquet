#!/usr/bin/env python3
"""SQL query through Python"""

import sys
import argparse
from time import time

from src.ensembl.production.sql_to_parquet.query import ConnectionMySQL, Query, logging
from src.ensembl.production.sql_to_parquet.config_json import Config

### Parse arguments
parser = argparse.ArgumentParser(description='Convert SQL to Parquet')
# Database config
parser.add_argument('--core_uri', type=str, help='Core database mysql URI')
parser.add_argument('--database', type=str, help='Connect to database')
parser.add_argument('--genome_uuid', type=str, help='Genome UUID')
parser.add_argument('--production_name', type=str, help='Production name')
# SQL config
parser.add_argument('--main_query', type=str, help='SQL query')
parser.add_argument('--query_config', type=str, help='Query JSON config')
# Writing Parquet
parser.add_argument('-o', type=str, default='.', help='Output directory')

def main():
    """ Convert SQL query to Parquet """
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    args = parser.parse_args()
    ## Read config
    query_config = Config(args.query_config).config_query()

    conn = ConnectionMySQL(core_uri = args.core_uri,
                database = args.database).connect()

    Query(engine = conn,
          prod_name = args.production_name,
          target_dir = args.o,
          data_type = query_config["data_type"],
          sql = args.main_query,
          supplementary_data = query_config["supplementary_data"]).execute()

if __name__ == "__main__":
    start = time()
    main()
    logging.info('Done, it took a total of %s sec(s).', (time()-start))
