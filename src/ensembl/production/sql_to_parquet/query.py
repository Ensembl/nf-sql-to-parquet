import os
import logging
import pandas as pd
from sqlalchemy import create_engine, bindparam, text
import pyarrow as pa
import pyarrow.parquet as pq

#### User-defined exception
class NoSpeciesException(Exception):
    """ Raised when no species ID and production name were defined"""

class InvalidQueryException(Exception):
    """Raised when query gives no output"""

#### Connector to database
class ConnectionMySQL:
    """ Create engine to connect to MySQL database """
    def __init__(self, core_uri, database):
        self.core_uri = core_uri.replace('mysql://', '')
        self.database = database

    def connect(self):
        """ Connect to MySQL database using SQLAlchemy """
        db_connection_str = f'mysql+pymysql://{self.core_uri}/{self.database}'
        engine = create_engine(db_connection_str)
        return engine

#### Queries
class Query:
    """ General functions for SQL queries """
    def __init__(self, engine, sql, target_dir, 
                 data_type, supplementary_data=None, lookup_key=None, species_id=None, prod_name=None):
        self.engine = engine
        try:
            if species_id is None and prod_name is None:
                raise NoSpeciesException
        except NoSpeciesException:
            logging.error('No species id or production name was given')
            raise
        self.species_id = species_id
        self._prod_name = prod_name
        self._sql = sql
        self.target_dir = target_dir
        self.supplementary_data = supplementary_data
        self.lookup_key = lookup_key
        self.data_type = data_type

    @property
    def prod_name(self):
        """" Retrieve production name using species_id if prod_name is not defined """
        if self._prod_name is None:
            logging.debug("Setting prod_name using species_id")
            t = """SELECT meta_value FROM meta
                WHERE meta_key = 'species.production_name' 
                AND species_id = :species_id"""
            stmt = text(t)
            stmt = stmt.bindparams(bindparam('species_id'))
            params = { 'species_id' : self.species_id }
            try:
                df = pd.read_sql(stmt, con=self.engine, params=params)
                if df.empty:
                    raise ValueError("Species ID is invalid")
            except ValueError as ve:
                logging.error('Value error: %s', ve)
                raise
            self._prod_name = df.iat[0,0]
        else:
            logging.debug("Checking prod_name validity")
            t = """SELECT meta_value FROM meta
                WHERE meta_key='species.production_name' 
                AND meta_value = :production_name"""
            stmt = text(t)
            stmt = stmt.bindparams(bindparam('production_name'))
            params = {'production_name': self._prod_name}
            try:
                df = pd.read_sql(stmt, con=self.engine, params=params)
                if df.empty:
                    raise ValueError("Production name is invalid")
            except ValueError as ve:
                logging.error('Value error: %s', ve)
                raise
        return self._prod_name
    
    @property
    def sql(self):
        """ read sql file """
        if self._sql.split('.')[-1] == 'sql':
            with open(self._sql, 'r') as sql_file:
                self._sql = sql_file.read()
        return self._sql

    @staticmethod
    def get_data(sql, engine, params = None):
        """ SQL query using SQLAlchemy """
        # try:
        df = pd.read_sql(sql, con=engine, params=params)
        if df.empty:
            logging.info('Query has no results')
        return df
    
    def supplementary_lookups(self):
        """ Build a dict containing supplementary lookups data """
        d = {}
        # Check if there are parameters for the query
        for key, val in self.supplementary_data.items():
            if isinstance(val, list):
                params = val[1]
                sql = val[0]
            else:
                sql = val
                params = None
            df = self.get_data(sql, engine=self.engine, params = params)
            df = df.dropna()
            df = df.groupby(df.columns[0]).agg(set)
            d[key] = df
        return d

    def write_parquet(self, df):
        """ Write dataframe in Parquet format """
        ## get path and name
        dir_path = os.path.join(self.target_dir, self.data_type, f'species={self.prod_name}')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        filename = self._prod_name + "_" + self.data_type + ".parquet"
        output = os.path.join(dir_path, filename)
        ## write
        table = pa.Table.from_pandas(df)
        pq.write_table(table, output)

    def execute(self):
        """ Get all the data and write a Parquet file """
        main_df = self.get_data(self.sql, self.engine, params={"production_name" : self.prod_name})
        if self.supplementary_data is not None:
            d = self.supplementary_lookups()
            # for i in self.lookup_key:
            for i in d.values():
                if not i.empty:
                    main_df = pd.merge(main_df, i, left_on=main_df.columns[0], right_index=True, how='left')
        main_df["species"] = self.prod_name
        self.write_parquet(main_df)