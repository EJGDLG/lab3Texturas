from obj import Obj
from MathLib import *
from texture import Texture

class Model(object):
    def __init__(self, filename):
        objFile = Obj(filename)
        
        self.vertices = objFile.vertices
        self.texCoords = objFile.texcoords
        self.faces = objFile.faces

        self.translate = [0, 0, 0]
        self.rotate = [0, 0, 0]
        self.scale = [1, 1, 1]

    def LoadTexture(self, filename):
        self.texture = Texture(filename)

    def GetModelMatrix(self):
        translateMat = TranslationMatrix(self.translate[0],
                                         self.translate[1],
                                         self.translate[2])
        rotateMat = RotationMatrix(self.rotate[0],
                                   self.rotate[1],
                                   self.rotate[2])
        scaleMat = ScaleMatrix(self.scale[0],
                               self.scale[1],
                               self.scale[2])

        print("translateMat:", translateMat)
        print("rotateMat:", rotateMat)
        print("scaleMat:", scaleMat)

        modelMatrix = matrix_mult(matrix_mult(translateMat, rotateMat), scaleMat)
        return modelMatrix
