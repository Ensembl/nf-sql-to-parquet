#  See the NOTICE file distributed with this work for additional information
#  regarding copyright ownership.
#
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import tempfile
import shutil
import unittest
from app.query import *

class TestQueries(unittest.TestCase):
    def setUp(self):
        ### disable all logging calls
        logging.disable(logging.CRITICAL)
        # logging.basicConfig(level=logging.DEBUG)

        ### SQLite setup
        self.engine = create_engine('sqlite:///:memory:', echo=True)
        cols = {"meta" : ["meta_id", "species_id", "meta_key", "meta_value"],
                "seq_region" : ["seq_region_id", "name", "coord_system_id", "length"],
                "coord_system" : ["coord_system_id", "species_id", "name", "version", "rank", "attrib"],
                "gene" : ['gene_id', 'biotype', 'analysis_id', 'seq_region_id', 'seq_region_start', 'seq_region_end', 
                         'seq_region_strand', 'display_xref_id', 'source', 'description', 'is_current', 
                         'canonical_transcript_id', 'stable_id', 'version', 'created_date', 'modified_date'],
                "gene_attrib" : ['gene_id', 'attrib_type_id', 'value'],
                "transcript" : ['transcript_id', 'gene_id', 'analysis_id', 'seq_region_id', 'seq_region_start', 'seq_region_end', 'seq_region_strand', 'display_xref_id', 'source', 'biotype', 'description', 'is_current', 'canonical_translation_id', 'stable_id', 'version', 'created_date', 'modified_date']
                }
        for key, value in cols.items():
            fname = f'/Users/sukanya/tests/sqlite/data/subset/{key}.txt.gz'
            df  = pd.read_csv(fname, header=None, sep="\t", low_memory=False)
            df.columns = value
            df = df.fillna('')
            df = df.replace('\\N', None)
            df.to_sql(name = key, con = self.engine)

        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        self.engine.dispose()
        shutil.rmtree(self.test_dir)

    ### Testing Query initialisation
    def test_empty_species(self):
        """ Assert that error is raised when no species is specified """
        with self.assertRaises(Exception):
            Query(engine=self.engine, sql="", target_dir=".", data_type="")
  
    ## Production name
    def test_set_prod_name(self):
        """ Test Query initialisation of production name """
        qu = Query(engine=self.engine, sql="", target_dir=".", data_type="", prod_name="homo_sapiens")
        self.assertEqual(qu.prod_name, 'homo_sapiens')

    def test_exception_prod_name(self):
        """ Assert that an error is raised when using a wrong production name """
        with self.assertRaises(ValueError):
            qu = Query(engine=self.engine, sql="", target_dir=".", data_type="", prod_name="foo")
            print(qu.prod_name)

    ## Species ID
    def test_get_prod_name_from_id(self):
        """ Test getting the production name from species_id """
        qu = Query(engine=self.engine, sql="", target_dir=".", data_type="", species_id=1)
        self.assertEqual(qu.prod_name, 'homo_sapiens')

    def test_exception_species_id(self):
        """ Assert that an error is raised when using a wrong species_id """
        with self.assertRaises(ValueError):
            qu = Query(engine=self.engine, sql="", target_dir=".", data_type="", species_id=10)
            print(qu.prod_name)

    ## SQL
    def test_get_sql(self):
        """ Test getting SQL """
        ## giving a SQL statement
        qu = Query(engine=self.engine, sql="SQL statement", target_dir=".", data_type="", species_id=1)
        self.assertEqual(qu.sql, "SQL statement", "Cannot read direct SQL statement")
        ## giving a .sql file
        tmp = tempfile.NamedTemporaryFile(suffix='.sql').name
        with open(tmp, "w") as f:
            f.write("SELECT * FROM meta")
            f.seek(0)
            qu2 = Query(engine=self.engine, sql=tmp, target_dir=".", data_type="", species_id=1)
            self.assertEqual(qu2.sql, "SELECT * FROM meta", "Cannot read SQL statement from .sql file")

    ### Testing queries
    def test_get_data(self):
        """ Test a simple query """
        qu = Query(engine=self.engine, sql="SELECT * FROM meta LIMIT 5;",
                   target_dir=".", data_type="", species_id=1)
        df = qu.get_data(qu.sql, qu.engine)
        self.assertFalse(df.empty, "Dataframe is empty")

    def test_supp_lookups(self):
        """ Test supplementary lookups with different paramstyle """
        sup = {"sup1" : """SELECT ga.gene_id, MAX(CASE WHEN ga.attrib_type_id=536 THEN ga.value END) AS ensembl_select
               FROM gene_attrib ga GROUP BY ga.gene_id""",
               "sup2" : ["""SELECT stable_id FROM transcript WHERE seq_region_strand = :strand""", {"strand" : 1}],
               "sup3" : ["""SELECT stable_id FROM transcript WHERE seq_region_strand = ?""", (1,)]}
        qu = Query(engine=self.engine, sql="", target_dir=".", data_type="", species_id=1, supplementary_data=sup)
        
        d = qu.supplementary_lookups()
        self.assertTrue(d)    

    def test_execute_with_lookups(self):
        """ Test supplementary lookups and final Parquet generation """
        sup = {"sup1" : """SELECT ga.gene_id, MAX(CASE WHEN ga.attrib_type_id=536 THEN ga.value END) AS ensembl_select
               FROM gene_attrib ga GROUP BY ga.gene_id""",
               "sup2" : ["""SELECT t.gene_id, t.stable_id as transcript_stable_id FROM transcript t 
                JOIN seq_region sr USING (seq_region_id)
                   JOIN coord_system cs USING (coord_system_id)
                   JOIN meta m ON (cs.species_id = m.species_id
                   AND m.meta_key = "species.production_name")
                   WHERE m.meta_value = ? LIMIT 20;""", ("homo_sapiens",)]}

        Query(engine=self.engine, 
                   sql="""SELECT gene_id FROM gene 
                   JOIN seq_region sr USING (seq_region_id)
                   JOIN coord_system cs USING (coord_system_id)
                   JOIN meta m ON (cs.species_id = m.species_id
                   AND m.meta_key = "species.production_name")
                   WHERE m.meta_value = :production_name LIMIT 20;""",
                   target_dir=self.test_dir,
                   data_type='gene', 
                   species_id=1, 
                   supplementary_data=sup, 
                   lookup_key=["sup1", "sup2"]).execute()
        filepath = os.path.join(self.test_dir, "homo_sapiens_gene.parquet")
        self.assertTrue(os.path.isfile(filepath))


if __name__ == "__main__":
    unittest.main()
