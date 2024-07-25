import pyarrow as pa

class GeneSchema:
    def __init__(self) -> None:
        self.schema = pa.schema([
            ('gene_id', pa.int64()),
            ('stable_id', pa.string()),
            ('region_name', pa.string()),
            ('start', pa.int64()),
            ('end', pa.int64()),
            ('strand', pa.int64()),
            ('biotype', pa.string()),
            ('source', pa.string()),
            ('gene_name', pa.string()),
            ('gene_symbol', pa.string()),
            ('nomenclature_symbol', pa.string()),
            ('nomenclature_provider', pa.string()),
            ('canonical_transcript', pa.string()),
            # Supplementary data columns
            ('transcript_stable_ids', pa.list_(pa.string())),
            ('translation_stable_ids', pa.list_(pa.string())),
            ('synonym', pa.list_(pa.string())),
            ('GC_content', pa.list_(pa.string())),
            ('havana_cv', pa.list_(pa.string())),
            ('proj_parent_gene', pa.list_(pa.string())),
            ('alternative_name', pa.list_(pa.string())),
            ('go_terms', pa.list_(pa.string())),
            # Partition column
            ('species', pa.string()),
        ])

class TranscriptSchema:
    def __init__(self) -> None:
        self.schema = pa.schema([
            ('transcript_id', pa.int64()),
            ('stable_id', pa.string()),
            ('region_name', pa.string()),
            ('start', pa.int64()),
            ('end', pa.int64()),
            ('strand', pa.int64()),
            ('biotype', pa.string()),
            ('source', pa.string()),
            ('description', pa.string()),
            ('transcript_symbol', pa.string()),
            # Supplementary data columns
            ('translation_stable_ids', pa.list_(pa.string())),
            ('miRNA_coordinates', pa.list_(pa.string())),
            ('frameshift', pa.list_(pa.string())),
            ('ncRNA', pa.list_(pa.string())),
            ('MANE_select', pa.list_(pa.string())),
            ('MANE_plus_clinical', pa.list_(pa.string())),
            ('go_terms', pa.list_(pa.string())),
            # Partition column
            ('species', pa.string()),
        ])

class TranslationSchema:
    def __init__(self) -> None:
        self.schema = pa.schema([
            ('translation_id', pa.int64()),
            ('stable_id', pa.string()),
            ('start', pa.int64()),
            ('end', pa.int64()),
            # Supplementary data columns
            ('go_terms', pa.list_(pa.string())),
            # Partition column
            ('species', pa.string()),
        ])

class ComparaSchema:
    def __init__(self) -> None:
        self.schema = pa.schema([
            ('homology_id', pa.int64()),
            ('description', pa.string()),
            ('type', pa.string()),
            ('dn', pa.float64()),
            ('ds', pa.float64()),
            ('goc_score', pa.int8()),
            ('wga_coverage', pa.float64()),
            ('is_high_confidence', pa.int8()),
            ('stable_id', pa.string()),
            ('perc_cov', pa.float64()),
            ('perc_id', pa.float64()),
            ('homolog_stable_id', pa.string()),
            ('homolog_species', pa.string()),
            ('homolog_perc_cov', pa.float64()),
            ('homolog_perc_id', pa.float64()),
            # Partition column
            ('species', pa.string())
        ])
