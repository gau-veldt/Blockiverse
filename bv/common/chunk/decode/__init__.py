"""
    Chunk decoding
"""
import zlib

def decompress(decoder):
    """
    Decorator to factor out chunk
    decompression logic from decoder routines
    """
    def wrapper(blob,origin):
        return decoder(zlib.decompress(blob),origin)
    return wrapper

from panda3d.core import Geom,GeomVertexFormat
from panda3d.core import GeomTriangles,GeomNode

@decompress
def Chunk2Geom(chunk,origin):
    """
    Decodes chunk into Panda3D geometry format
    """
    # determine where chunk should be placed in world space
    orgX=origin[0]
    orgY=origin[1]
    orgZ=origin[2]
    # determine chunk's coordinate
    chunkX=orgX/16
    chnukY=orgY/16
    # generate name tags for the various parts
    chunkId="%s_%s" % (chunkX,chunkY)
    vtxName="vtx_%s" % chunkId
    nodeName="node_%s" % chunkId
    # TODO: read chunk data and generate triangles

if __name__ == '__main__':
    pass
