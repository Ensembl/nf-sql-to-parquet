-- parquet gene table
SELECT
    g.gene_id,
    IF(ISNULL(g.version), g.stable_id, concat(g.stable_id, '.', g.version)) AS stable_id,
    sr.name AS region_name,
    g.seq_region_start AS start,
    g.seq_region_end AS end,
    g.seq_region_strand AS strand,
    g.biotype,
    g.source,
    g.description AS gene_name,
    x.display_label AS gene_symbol,
    x.dbprimary_acc AS nomenclature_symbol,
    edb.db_display_name AS nomenclature_provider,
    ct.stable_id AS canonical_transcript
FROM
    gene g
    JOIN seq_region sr USING (seq_region_id)
    JOIN coord_system cs USING (coord_system_id)
    LEFT JOIN xref x ON (g.display_xref_id = x.xref_id)
    LEFT JOIN external_db edb ON (x.external_db_id = edb.external_db_id)
    JOIN transcript ct ON (g.canonical_transcript_id = ct.transcript_id)
    JOIN meta m ON (
        cs.species_id = m.species_id
        AND m.meta_key = "species.production_name"
    )
WHERE
    m.meta_value = %(production_name)s