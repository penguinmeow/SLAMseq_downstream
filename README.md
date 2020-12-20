**Pipeline**
1. Fastqc to see the quality of raw fastqc reads
2. Trimmomatic to trim the adapters
3. python /home/xzhen/pipelines/slamseq/submit_slamdunk.py 
--in-dir pytest 
--reference GRCm38.p6.genome.fa 
--bed UTR/3pUTR.bed 
--out-dir pytest

4. cp out_dir/*/count/*.tsv /output
5. prepare a list of sample names
6. Rscript prepare_for_netbid2.R
7. Further NetBID analysis


# SLAMseq_downstream
Alleyoop and NetBID
