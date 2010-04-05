from BagType import Bag
import itertools

def ptt_parser(ptt_fp):
    """
    Parse PTT annotation files from NCBI.
    """
    for line in itertools.islice(ptt_fp, 3, None):
        line = line.strip().split('\t')
        coords, strand, _, PID, gene, syn, code, cog, product = line

        start, stop = coords.split('..')
        start = int(start) - 1
        stop = int(stop) - 1
        orientation = +1
        if strand == '-':
            orientation = -1

        b = Bag(start=start, stop=stop, orientation=orientation, PID=PID,
                gene=gene, synonym=syn, code=code, cog=cog,
                description=product)

        yield b
