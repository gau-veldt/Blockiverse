"""
    Chunk decoding
"""
import zlib

def decompress(decoder):
    """
    Decorator to factor out chunk
    decompression logic from decoder routines
    """
    def wrapper(blob,origin,viewpoint):
        return decoder(zlib.decompress(blob),origin,viewpoint)
    return wrapper

from panda3d.core import Geom,GeomVertexFormat
from panda3d.core import GeomTriangles,GeomNode

@decompress
def Chunk2Geom(chunk,origin,viewpoint):
    """
    Decodes chunk into Panda3D geometry format
    @param
        chunk: encoded chunk
        origin: chunk destination in world coordinates
        viewpoint: viewer reference point in world coordinates
                    (used for LOS culling of non-visible blocks
                    to reduce triangle load)
    @return
        A panda3D Node object translated appropriately to place
        the decoded chunk correctly within the world.
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
