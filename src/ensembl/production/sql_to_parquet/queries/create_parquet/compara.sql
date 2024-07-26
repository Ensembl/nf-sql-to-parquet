-- compara
select 
h.homology_id, 
h.description, 
method_link.type,
h.dn, 
h.ds,
h.goc_score, 
h.wga_coverage, 
h.is_high_confidence,
IF(ISNULL(gm1.version), gm1.stable_id, concat(gm1.stable_id, '.', gm1.version)) as stable_id, 
hm1.perc_cov as perc_cov, hm1.perc_id as perc_id, 
IF(ISNULL(gm2.version), gm2.stable_id, concat(gm2.stable_id, '.', gm2.version)) as homolog_stable_id, 
gd2.name as homolog_species, 
hm2.perc_cov as homolog_perc_cov, hm2.perc_id as homolog_perc_id

from homology h

join homology_member hm1 on (hm1.homology_id = h.homology_id)
join gene_member gm1 on (gm1.gene_member_id = hm1.gene_member_id)

join homology_member hm2 on (hm2.homology_id = h.homology_id and  hm2.gene_member_id <> hm1.gene_member_id)
join ensembl_compara_references_mvp.gene_member gm2 on (gm2.gene_member_id = hm2.gene_member_id)
join ensembl_compara_references_mvp.genome_db gd2 on (gd2.genome_db_id = gm2.genome_db_id)

join method_link_species_set using (method_link_species_set_id) 
join method_link using (method_link_id)