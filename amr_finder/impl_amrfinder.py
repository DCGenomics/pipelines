import argparse
import os
import subprocess
import sys
import tempfile
import yaml

def print_versions():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    revision = "Unknown\n"
    r = subprocess.run(["svn", "info", "--show-item", "revision"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode == 0:
        revision = r.stdout.decode()
    print("CWL Subversion Revision", revision, end='')
    print("Docker Container Versions:")
    subprocess.run("grep -hPo '(?<=dockerPull: )(.*)(?=$)' *.cwl | sort -u | awk '{printf(\"    %s\\n\", $1)}'", shell=True)

class cwlgen:
    def __init__(self, args):
        self.args = args
        self.parse_deflines = True
        if self.args.no_parse_deflines:
            self.parse_deflines = False

    def params(self):
        params =  {
            'query': {                                                      
                'class': 'File',
                'location': os.path.realpath(self.args.fasta)
            },
            'parse_deflines': self.parse_deflines
        }
        #param_file = 'amrfinder_params.yaml'
        #stream = open(param_file, 'w')
        (fdstream, self.param_file) = tempfile.mkstemp(suffix=".cwl", prefix="amr_params_")
        stream = os.fdopen(fdstream, 'w')
        print(self.param_file)
        yaml.dump(params, stream)
        #print(yaml.dump(params))

    def run(self):
        script_path = os.path.dirname(os.path.realpath(__file__))
        cwlscript = script_path + "/wf_amr_prot.cwl"

        if self.args.show_output:
            cwl = subprocess.run(['cwltool', cwlscript, self.param_file])
        else:
            cwl = subprocess.run(['cwltool', cwlscript, self.param_file],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        for line in open('output.txt','r'):
            print(line, end='')

        self.cleanup()    

    def cleanup(self):
        def safe_remove(f):
            if os.path.exists(f):
                os.remove(f)
        safe_remove(self.param_file)

        # Cleanup after cwltool's use of py2py3
        safe_remove('/tmp/futurized_code.py')
        safe_remove('/tmp/original_code.py')
        safe_remove('/tmp/py2_detection_code.py')
            
def run(updater_parser):
    parser = argparse.ArgumentParser(
        parents=[updater_parser],
        description='Run (and optionally update) the amr_finder pipeline.')

    parser.add_argument('-npd', '--no_parse_deflines', action='store_true',
                        help='Do not use -parse_deflines option for blast (sometimes fixes issues with format of the input FASTA file being automatically parsed by BLAST)')
    parser.add_argument('-o',   '--output',            dest='outfile',    help='tabfile output to this file instead of STDOUT')

    # Options relating to protein input (-p):
    #parser.add_argument('-f <out.fa> FASTA file containing proteins identified as candidate AMR genes
    #parser.add_argument('-g <gff> GFF file indicating genomic location for proteins in -p <protein>
    # Options relating to nucleotide sequence input (-n)
    #parser.add_argument('-i <0.9> Minimum proportion identical translated AA residues
    #parser.add_argument('-c <0.5> Minimum coverage of reference protein sequence
    #parser.add_argument('-t <11> Translation table for blastx

    parser.add_argument('-s', '--show_output', action='store_true',  help='Show the stdout and stderr output from the pipeline execution.')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--protein',    action='store_true',   help='Amino-acid sequences to search using BLASTP and HMMER')
    group.add_argument('-n', '--nucleotide', action='store_false',  help='genomic sequence to search using BLASTX')
    parser.add_argument('fasta', help='FASTA file containing the query sequence(s).')
    args = parser.parse_args()

    if args.version:
        print_versions()
        sys.exit()
    
    g = cwlgen(args)
    g.params()
    g.run()
    
        
    
