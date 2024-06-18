-- table_name = "translation"
SELECT
    tr.stable_id,
    tr.seq_start as start,
    tr.seq_end as end
FROM
    translation tr
    JOIN transcript t on (tr.transcript_id = t.transcript_id)
    JOIN seq_region sr ON (t.seq_region_id = sr.seq_region_id)
    JOIN coord_system cs ON (sr.coord_system_id = cs.coord_system_id)
    JOIN meta m on (
        cs.species_id = m.species_id
        and m.meta_key = "species.production_name"
    )
WHERE
    m.meta_value = %s