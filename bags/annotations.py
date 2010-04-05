import os
from pygr import sqlgraph, annotation as anno
sqlite = sqlgraph.import_sqlite()

CREATE_SCHEMA = '''CREATE TABLE annotations
    (k INTEGER PRIMARY KEY,
     name TEXT,
     seq_id TEXT,
     start INT,
     stop INT,
     orientation INT,
     description TEXT);
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

        self.filename = filename
        self.conn = conn
        self.cursor = c

    def add(self, info, seq_id):
        c = self.cursor
        c.execute('''INSERT INTO annotations (name, seq_id, start, stop,
                     orientation, description)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (info.gene, seq_id, info.start, info.stop, info.orientation,
                   info.description))

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
