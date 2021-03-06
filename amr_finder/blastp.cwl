cwlVersion: v1.0
class: CommandLineTool
hints:
  DockerRequirement:
    dockerPull: ncbi/blast_amr:18.02

baseCommand: blastp
#stdout: $(inputs.db).out
stdout: blastp.out
inputs:
  query:
    type: File
    inputBinding:
      prefix: -query
  db:
    type: string
    default: AMRProt
    inputBinding:
      prefix: -db
  outfmt:
    type: string?
    default: "6 qseqid sseqid length nident qstart qend qlen sstart send slen qseq"
    inputBinding:
      prefix: -outfmt
  show_gis:
    type: boolean
    default: true
    inputBinding:
      prefix: -show_gis
  word_size:
    type: int?
    default: 6
    inputBinding:
      prefix: -word_size
  threshold:
    type: int?
    default: 21
    inputBinding:
      prefix: -threshold
  evalue:
    type: double?
    default: 1e-20
    inputBinding:
      prefix: -evalue
  comp_based_stats:
    type: int?
    default: 0
    inputBinding:
      prefix: -comp_based_stats
  parse_deflines:
    type: boolean?
    default: true
    inputBinding:
      prefix: -parse_deflines

outputs:
  - id: output
    type: File
    outputBinding:
      glob: "blastp.out"
