import os
from pygr import sqlgraph, annotation as anno
sqlite = sqlgraph.import_sqlite()

CREATE_SCHEMA = '''CREATE TABLE annotations
    (syn TEXT PRIMARY KEY,
     name TEXT,
     seq_id TEXT,
     start INT,
     stop INT,
     orientation INT,
     description TEXT,
     type TEXT DEFAULT 'gene');
'''

CREATE_SCHEMA_IG = '''CREATE TABLE ig_annotations
    (k INTEGER PRIMARY KEY,
     prev_gene_id INT,
     next_gene_id INT,
     name TEXT,
     seq_id TEXT,
     start INT,
     stop INT,
     type TEXT DEFAULT 'intergenic');
'''


class BagsAnnotationMaker(object):

    def __init__(self, filename, initialize=True):
        if initialize:
            try:
                os.unlink(filename)
            except OSError:
                pass

        conn = sqlite.connect(filename)
        c = conn.cursor()

        try:
            c.execute(CREATE_SCHEMA)
        except sqlite.OperationalError:
            pass
        
        try:
            c.execute(CREATE_SCHEMA_IG)
        except sqlite.OperationalError:
            pass

        self.filename = filename
        self.conn = conn
        self.cursor = c

    def add_gene(self, info, seq_id):
        c = self.cursor
        c.execute('''INSERT INTO annotations (syn, name, seq_id, start, stop,
                     orientation, description)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (info.synonym, info.gene, seq_id, info.start, info.stop, info.orientation,
                   info.description))

    def add_ig(self, prev_gene, start, next_gene, stop, name, seq_id):
        c = self.cursor
        c.execute('''INSERT INTO ig_annotations (prev_gene_id, next_gene_id, name, seq_id, start, stop)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (prev_gene, next_gene, name, seq_id, start, stop))

    def close(self):
        self.conn.commit()
        self.conn.close()

    def get_annodb(self, genome, annotationType='sql:'):
        slicedb = sqlgraph.SQLTable('annotations',
                                    serverInfo=sqlgraph.SQLiteServerInfo(self.filename))

        annodb = anno.AnnotationDB(slicedb, genome,
                                   annotationType=annotationType,
                                   sliceAttrDict=dict(id='seq_id'))
        return annodb

    def get_ig_annodb(self, genome, annotationType='sql:'):
        slicedb = sqlgraph.SQLTable('ig_annotations',
                                    serverInfo=sqlgraph.SQLiteServerInfo(self.filename))

        annodb = anno.AnnotationDB(slicedb, genome,
                                   annotationType=annotationType,
                                   sliceAttrDict=dict(id='seq_id'))
        return annodb
