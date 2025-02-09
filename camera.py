from MathLib import matrix_mult, TranslationMatrix, RotationMatrix, matrix_inv

class Camera(object):
    def __init__(self):
        self.translate = [0, 0, 0]
        self.rotate = [0, 0, 0]

    def GetViewMatrix(self):
        # Crear matrices de traducción y rotación
        translateMat = TranslationMatrix(self.translate[0],
                                         self.translate[1],
                                         self.translate[2])

        rotateMat = RotationMatrix(self.rotate[0],
                                   self.rotate[1],
                                   self.rotate[2])

        # Multiplicar matrices
        camMatrix = matrix_mult(translateMat, rotateMat)

        # Invertir la matriz
        return matrix_inv(camMatrix)
