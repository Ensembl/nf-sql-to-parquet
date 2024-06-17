#!/usr/bin/env python3
"""SQL query through Python"""

import sys
import argparse
from time import time

from query import ConnectionMySQL, Query, logging
from config_json import Config

### Parse arguments
parser = argparse.ArgumentParser(description='SQL to Parquet')
# Species
parser.add_argument('-s', type=int, default=None, help='Species ID')
parser.add_argument('-pn', type=str, default=None, help='Production name')
# Database config
parser.add_argument('-sc', type=str, help='Species and database config JSON format')
# SQL config
parser.add_argument('-q', type=str, help='SQL query')
parser.add_argument('-qc', type=str, help='Query JSON config')
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
    connection = Config(args.sc).config_species()
    data = Config(args.qc).config_query()

    conn = ConnectionMySQL(host = connection["host"],
                user = connection["user"],
                database = connection["database"],
                port = connection["port"],
                password = connection["password"]).connect()

    Query(engine = conn,
          species_id = args.s,
          prod_name = args.pn,
          target_dir = args.o,
          data_type = data["data_type"],
          sql = args.q,
          supplementary_data = data["supplementary_data"],
          lookup_key = data["lookup_key"]).execute()

if __name__ == "__main__":
    start = time()
    main()
    logging.info('Done, it took a total of %s sec(s).', (time()-start))
