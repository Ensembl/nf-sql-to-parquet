SELECT
    t.transcript_id,
    IF(ISNULL(t.version), t.stable_id, concat(t.stable_id, '.', t.version)) AS stable_id,
    sr.name as region_name,
    t.seq_region_start as start,
    t.seq_region_end as end,
    t.seq_region_strand as strand,
    t.biotype,
    t.source,
    t.description,
    x.display_label as transcript_symbol
FROM
    transcript t
    JOIN seq_region sr ON (t.seq_region_id = sr.seq_region_id)
    JOIN coord_system cs ON (sr.coord_system_id = cs.coord_system_id)
    LEFT JOIN xref x on (t.display_xref_id = x.xref_id)
    LEFT JOIN external_db edb ON (x.external_db_id = edb.external_db_id)
    JOIN meta m on (
        cs.species_id = m.species_id
        and m.meta_key = "species.production_name"
    )
WHERE
    m.meta_value = %(production_name)s