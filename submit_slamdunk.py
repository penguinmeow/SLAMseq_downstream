#!/usr/bin/env python

# Script to submit slam-seq jobs in parallel

import glob
import subprocess
import re
import os
import sys
import argparse
sys.path.append("/home/xzhen/pipelines/slamseq")
from encode_lib_common import (
    copy_f_to_dir, copy_f_to_f, log, ls_l, mkdir_p, read_tsv, rm_f,
    run_shell_cmd, strip_ext_fastq)

def parse_arguments():
    parser = argparse.ArgumentParser(prog='Wrapper for BSUB job submission for SLAM-seq data.', description='')
    parser.add_argument('--in-dir', default='', type=str, help= 'Path to FASTQ files.')
    #parser.add_argument('--adapters',default='/home/xzhen/adapters/TruSeqAdapters3.PE.fa', type=str, help='Fasta file of adapter sequences')
    parser.add_argument('--suffix', default='fastq.gz', type=str, help= 'Path to reference genome fasta file.')
    parser.add_argument('--reference', default='', type=str, help= 'Path to reference genome fasta file.')
    parser.add_argument('--bed', default='', type=str, help= 'Path to 3 prime UTR files.')
    parser.add_argument('--threads', default='16', type=str, help= 'The number of threads to use for this dunk.')
    parser.add_argument('--memory', default='6GB', type=str, help= 'Memory requested to run the analysis.')
    parser.add_argument('--queue', default='standard', type=str,help='Queue to submit the job in HPCF (use bqueues to choose).')
    parser.add_argument('--out-dir', default='slamdunk_out', type=str,help='Output Directory.')
    parser.add_argument('--log-level', default='INFO',
                        choices=['NOTSET', 'DEBUG', 'INFO',
                                 'WARNING', 'CRITICAL', 'ERROR',
                                 'CRITICAL'],
                        help='Log level')

    args = parser.parse_args()
    log.setLevel(args.log_level)
    log.info(sys.argv)
    return args

#read parameter
args = parse_arguments()
log.info('Initializing and creating Output directory...')
mkdir_p(args.out_dir)

#collect all input fasta R1
fq = args.in_dir+'/*{}'
fastqR1 = glob.glob(fq.format(args.suffix))

#what is < means?
hpcfsubmit = 'bsub ' + '-R ' + '"rusage[mem=' + args.memory + ']" ' + '-q ' + args.queue + ' < '
#print 'Job submitted with command: {}'.format(hpcfsubmit)


def create_job_file(fastq, reference, bed, out_dir, threads):
    basename = os.path.basename(strip_ext_fastq(fastq))
    prefix = os.path.join(out_dir,basename)

    job_header = '#!/bin/bash\n'
    job_header += '#BSUB -P SLAMseq\n'
    job_header += '#BSUB -J {}_SLAMseq\n'
    job_header += '#BSUB -oo {}'+'/SLAMDUNKlog.out\n'
    job_header += '#BSUB -eo {}'+'/SLAMDUNKlog.err\n'
    job_header += '#BSUB -n 2\n'
    job_header += '#BSUB -N xzhen@stjude.org\n'
    job_header = job_header.format(basename,prefix, prefix)

    ### Load all the required module for analysis:
    moduleload = 'module load conda3/5.1.0\n'

    job_body1 = ''
    job_body2 = ''

    ### Write job body to run each wrapper for the sample:
    job_body1 = 'source activate slamseq'

    job_body2 = 'slamdunk all -r {} -b {} -o {} -t {} {} '
    job_body2 = job_body2.format(reference, bed, out_dir, threads, fastq)

    jobfile = prefix + ".sh"
    with open(jobfile,"w") as new_file:
        new_file.write(job_header + moduleload + job_body1 + '\n' + job_body2 + '\n')
        return jobfile


def submit_job(jobf):
    os.system('{}'.format(hpcfsubmit) + jobf)

log.info('Generating job file for each sample and submitting jobs....')

for fastq in range(0,len(fastqR1)):
    submit_job(create_job_file(fastqR1[fastq], args.reference, args.bed, args.out_dir, args.threads))
