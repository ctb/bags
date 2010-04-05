#! /usr/bin/env python
import sys, os
import pygr
print pygr
from pygr import seqdb, cnestedlist, sqlgraph, annotation
import itertools
import sqlite3
from pygr.sqlgraph import SQLiteServerInfo

ptt_file = os.path.realpath(sys.argv[1])
genome_file = os.path.realpath(sys.argv[2])
sql_file = ptt_file + '.sqldb'

genome = seqdb.SequenceFileDB(genome_file)
seq_id = genome.keys()[0]

ptt_fp = open(ptt_file)

try:
    os.unlink(sql_file)
except OSError:
    pass
sqldb = sqlite3.connect(sql_file)
c = sqldb.cursor()

c.execute('CREATE TABLE annotations (k INTEGER PRIMARY KEY, name TEXT, seq_id TEXT, start INT, stop INT, orientation INT);')

for n, line in enumerate(itertools.islice(ptt_fp, 3, None)):
    line = line.split('\t')
    coords, strand, _, _, gene, syn, _, _, _ = line

    start, stop = coords.split('..')
    start = int(start) - 1
    stop = int(stop) - 1
    orientation = +1
    if strand == '-':
        orientation = -1

    if gene == '-':
        gene = syn

    c.execute('INSERT INTO annotations (name, seq_id, start, stop, orientation) VALUES (?, ?, ?, ?, ?)', (gene, seq_id, start, stop, orientation))

sqldb.commit()

print 'added', n, 'records'

### create

slicedb = sqlgraph.SQLTable('annotations',
                            serverInfo=SQLiteServerInfo(sql_file))

annodb = annotation.AnnotationDB(slicedb, genome, annotationType='sql:',
                                 sliceAttrDict=dict(id='seq_id'))

### save

from pygr import worldbase

genome.__doc__ = 'Campy genome'
worldbase.Bio.campy.genome = genome

annodb.__doc__ = 'Campy gene annotations from NCBI (PTT)'
worldbase.Bio.campy.genes = annodb

nlmsa = cnestedlist.NLMSA('genes_map', 'w', pairwiseMode=True)
for v in annodb.itervalues():
    nlmsa.addAnnotation(v)
nlmsa.build(saveSeqDict=False)
    
nlmsa.__doc__ = 'Campy gene mapping from NCBI'
worldbase.Bio.campy.gene_map = nlmsa

worldbase.commit()
