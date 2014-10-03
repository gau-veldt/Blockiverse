"""
    Chunk decoding
"""
import zlib

def decompress(decoder):
    """
    Decorator to factor out chunk
    decompression logic from decoder routines
    """
    def wrapper(self,blob,origin):
        return decoder(self,zlib.decompress(blob),origin)
    return wrapper

from panda3d.core import Geom,GeomVertexFormat,GeomVertexData
from panda3d.core import GeomTriangles,GeomNode,GeomVertexWriter

class Chunk2GeomDecoder:
    """
        Chunk decoder that decodes chunks to Panda3D Geoms/Nodes
    """
    def __init__(self):
        self.textures={}
        tex=loader.loadTexture("testPat.png")
        self.textures[1]=tex
        self.viewPoint=(0,0,0)
        self.cubeVtxSrc=[
            # 14 vertices per cube mapped
            # so that UV coords utilize
            # the typical cube unwrap:
            #
            #   ####  <-- square texture
            #   ##U#
            #   BLFR
            #   ##D#    #=unused
            #
            # This form uses 14 vertices per cube since
            # the extra (worldspace overlapped) vertices
            # map different U,V coordinates at the same
            # worldspace coordinates, depending on face
            #   
            # x    y    z    u    v
            (1.00,1.00,1.00,0.00,0.50), # A
            (1.00,1.00,0.00,0.00,0.25), # B
            (0.00,1.00,1.00,0.25,0.50), # C
            (0.00,1.00,0.00,0.25,0.25), # D
            (0.00,0.00,1.00,0.50,0.50), # E
            (0.00,0.00,0.00,0.50,0.25), # F
            (1.00,0.00,1.00,0.75,0.50), # G
            (1.00,0.00,0.00,0.75,0.25), # H
            (1.00,1.00,1.00,1.00,0.50), # I
            (1.00,1.00,0.00,1.00,0.25), # J
            (0.00,1.00,1.00,0.50,0.75), # K
            (1.00,1.00,1.00,0.75,0.75), # L
            (0.00,1.00,0.00,0.50,0.00), # M
            (1.00,1.00,0.00,0.75,0.00)  # N
            ]
        self.triSrc=[
            #
            #  Faces (QUAD/TRIPAIR)
            #  using RHR vertex ordering for
            #  correct face surface normals
            #
            #    front: EFHG/EFH+HGE
            #     rear: CABD/CAB+BDC
            #     left: CDFE/CDF+FEC
            #    right: GHJI/GHJ+JIG
            #    upper: KEGL/KEG+GLK
            #    lower: FMNH/FMN+NHF
            #
            "EFH","HGE",
            "CAB","BDC",
            "CDF","FEC",
            "GHJ","JIG",
            "KEG","GLK",
            "FMN","NHF"
            ]
        #
        # setup cube
        #
        # one cube node will be generated per non-air block
        # since different block id's potentially refer to
        # different textures and thus must be separate nodes
        # of the scene graph.
        #
        #   1. vertices
        self.cubeVtx=GeomVertexData('blockCube',GeomVertexFormat.getV3t2(),Geom.UHStatic)
        self.cubeVtx.setNumRows(len(self.cubeVtxSrc))
        vtxW=GeomVertexWriter(self.cubeVtx,'vertex')
        txcW=GeomVertexWriter(self.cubeVtx,'texcoord')
        for vertex in self.cubeVtxSrc:
            vtxW.addData3f(*vertex[0:3])
            txcW.addData2f(*vertex[3:5])
        #   2. mesh
        self.cubeMesh=GeomTriangles(Geom.UHStatic)
        for tri in self.triSrc:
            for triV in tri:
                triVtxId=ord(triV)-65 # changea 'A'-'N' to 0-13
                self.cubeMesh.addVertex(triVtxId)
            self.cubeMesh.close_primitive()
        #   3. geometry (primitive+vertex pair)
        self.cubeGeom=Geom(self.cubeVtx)
        self.cubeGeom.addPrimitive(self.cubeMesh)

    def setViewpoint(x,y,z):
        self.viewPoint=(x,y,z)

    @decompress
    def Chunk2Geom(self,sChunk,origin):
        """
        Decodes chunk into Panda3D geometry format
        @param
            sChunk: encoded chunk
            origin: chunk location in world as 3-tuple
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
        chunkY=orgY/16
        # generate name tags for the various parts
        chunkId="%s_%s" % (chunkX,chunkY)
        vtxName="vtx_%s" % chunkId
        nodeName="chunk_%s" % chunkId
        # create empty node for entire chunk
        chunkNode=render.attachNewNode(nodeName)
        # convert string chunk to numeric
        chunk=[ord(c) for c in sChunk]
        # TODO: read chunk data and generate cube nodes
        flags=chunk[0]+(chunk[1]<<8)+(chunk[2]<<16)+(chunk[3]<<24)
        chunk=chunk[4:] # remove biome/flagbits
        for cY in range(16):
            for cX in range(16):
                for cZ in range(256):
                    cell=cZ+(cX<<8)+(cY<<12)
                    # lookup neighbours
                    me=chunk[cell]
                    if me>0:
                        n_up=chunk[cell-1]    if cZ>0   else 0
                        n_dn=chunk[cell+1]    if cZ<255 else 0
                        n_lt=chunk[cell-256]  if cX>0   else 0
                        n_rt=chunk[cell+256]  if cX<15  else 0
                        n_bk=chunk[cell-4096] if cY>0   else 0
                        n_fd=chunk[cell+4096] if cY<15  else 0
                        if n_up==0 or n_dn==0 or \
                           n_lt==0 or n_rt==0 or \
                           n_bk==0 or n_fd==0:
                            # for any non-obscured block
                            # generate a cube
                            block=GeomNode("%s_block_%s_%s_%s"%(nodeName,cX,cY,cZ))
                            block.addGeom(self.cubeGeom)
                            blockNode=chunkNode.attachNewNode(block)
                            blockNode.setTexture(self.textures[me])
                            blockNode.setPos(cX,cY,cZ)
        chunkNode.setPos(chunkX*16,chunkY*16,-64)
        return chunkNode

if __name__ == '__main__':
    pass
