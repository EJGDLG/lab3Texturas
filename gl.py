import struct
from camera import Camera
from math import tan, pi
from MathLib import barycentricCoords, matrix_mult, TranslationMatrix, ScaleMatrix, RotationMatrix

def char(c):
    return struct.pack("=c", c.encode("ascii"))

def word(w):
    return struct.pack("=h", w)

def dword(d):
    return struct.pack("=l", d)

POINTS = 0
LINES = 1
TRIANGLES = 2

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.camera = Camera()
        self.glViewport(0, 0, self.width, self.height)
        self.glProjection()

        self.glColor(1, 1, 1)
        self.glClearColor(0, 0, 0)
        self.glClear()

        self.vertexShader = None
        self.fragmentShader = None

        self.activeTexture = None
        self.primitiveType = TRIANGLES
        self.models = []

    def glViewport(self, x, y, width, height):
        self.vpX = int(x)
        self.vpY = int(y)
        self.vpWidth = width
        self.vpHeight = height

        self.viewportMatrix = [
            [width / 2, 0, 0, x + width / 2],
            [0, height / 2, 0, y + height / 2],
            [0, 0, 0.5, 0.5],
            [0, 0, 0, 1]
        ]

    def glProjection(self, n=0.1, f=1000, fov=60):
        aspectRatio = self.vpWidth / self.vpHeight
        fov *= pi / 180
        t = tan(fov / 2) * n
        r = t * aspectRatio

        self.projectionMatrix = [
            [n / r, 0, 0, 0],
            [0, n / t, 0, 0],
            [0, 0, -(f + n) / (f - n), -(2 * f * n) / (f - n)],
            [0, 0, -1, 0]
        ]

    def glColor(self, r, g, b):
        self.currColor = [min(1, max(0, r)), min(1, max(0, g)), min(1, max(0, b))]

    def glClearColor(self, r, g, b):
        self.clearColor = [min(1, max(0, r)), min(1, max(0, g)), min(1, max(0, b))]

    def glClear(self):
        color = [int(i * 255) for i in self.clearColor]
        self.screen.fill(color)
        self.frameBuffer = [[self.clearColor for _ in range(self.height)] for _ in range(self.width)]
        self.zbuffer = [[float('inf') for _ in range(self.height)] for _ in range(self.width)]

    def glPoint(self, x, y, color=None):
        x = round(x)
        y = round(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            color = [int(i * 255) for i in (color or self.currColor)]
            self.screen.set_at((x, self.height - 1 - y), color)
            self.frameBuffer[x][y] = color

    def glLine(self, v0, v1, color=None):
        x0, y0 = v0
        x1, y1 = v1
        if x0 == x1 and y0 == y1:
            self.glPoint(x0, y0, color)
            return

        dy, dx = abs(y1 - y0), abs(x1 - x0)
        steep = dy > dx
        if steep:
            x0, y0, x1, y1 = y0, x0, y1, x1
        if x0 > x1:
            x0, x1, y0, y1 = x1, x0, y1, y0

        dy, dx = abs(y1 - y0), abs(x1 - x0)
        offset, limit = 0, 0.75
        m, y = dy / dx, y0

        for x in range(round(x0), round(x1) + 1):
            if steep:
                self.glPoint(y, x, color)
            else:
                self.glPoint(x, y, color)

            offset += m
            if offset >= limit:
                y += 1 if y0 < y1 else -1
                limit += 1

    def glGenerateFrameBuffer(self, filename):
        with open(filename, "wb") as file:
            file.write(char("B"))
            file.write(char("M"))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))

            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            for y in range(self.height):
                for x in range(self.width):
                    color = self.frameBuffer[x][y]
                    color = bytes([color[2], color[1], color[0]])
                    file.write(color)

    def glRender(self):
        for model in self.models:
            mMat = model.GetModelMatrix()
            self.activeTexture = model.texture
            vertexBuffer = []

            for face in model.faces:
                faceVerts = []
                for i in range(len(face)):
                    vert = list(model.vertices[face[i][0] - 1])
                    if self.vertexShader:
                        vert = self.vertexShader(
                            vert,
                            modelMatrix=mMat,
                            viewMatrix=self.camera.GetViewMatrix(),
                            projectionMatrix=self.projectionMatrix,
                            viewportMatrix=self.viewportMatrix
                        )
                    vert.extend(model.texCoords[face[i][1] - 1])
                    if len(vert) < 5:
                        raise ValueError("Cada vértice debe tener al menos 5 componentes")
                    faceVerts.append(vert)

                if len(faceVerts) == 3:
                    vertexBuffer.extend(faceVerts[0])
                    vertexBuffer.extend(faceVerts[1])
                    vertexBuffer.extend(faceVerts[2])
                elif len(faceVerts) == 4:
                    vertexBuffer.extend(faceVerts[0])
                    vertexBuffer.extend(faceVerts[2])
                    vertexBuffer.extend(faceVerts[3])

            self.glDrawPrimitives(vertexBuffer, 5)

    def glTriangle(self, A, B, C):
        if A[1] < B[1]: A, B = B, A
        if A[1] < C[1]: A, C = C, A
        if B[1] < C[1]: B, C = C, B

        def flatBottom(vA, vB, vC):
            try:
                mBA, mCA = (vB[0] - vA[0]) / (vB[1] - vA[1]), (vC[0] - vA[0]) / (vC[1] - vA[1])
            except ZeroDivisionError:
                return
            if vB[0] > vC[0]: vB, vC = vC, vB
            x0, x1 = vB[0], vC[0]
            for y in range(round(vB[1]), round(vA[1] + 1)):
                for x in range(round(x0 - 1), round(x1 + 1)):
                    self.glDrawTrianglePoint(vA, vB, vC, [x, y])
                x0 += mBA
                x1 += mCA

        def flatTop(vA, vB, vC):
            try:
                mCA, mCB = (vC[0] - vA[0]) / (vC[1] - vA[1]), (vC[0] - vB[0]) / (vC[1] - vB[1])
            except ZeroDivisionError:
                return
            if vA[0] > vB[0]: vA, vB = vB, vA
            x0, x1 = vA[0], vB[0]
            for y in range(round(vC[1]), round(vA[1] + 1)):
                for x in range(round(x0 - 1), round(x1 + 1)):
                    self.glDrawTrianglePoint(vA, vB, vC, [x, y])
                x0 += mCA
                x1 += mCB

        if B[1] == C[1]:
            flatBottom(A, B, C)
        elif A[1] == B[1]:
            flatTop(A, B, C)
        else:
            D = [A[0] + (B[1] - A[1]) / (C[1] - A[1]) * (C[0] - A[0]), B[1], 0]
            flatBottom(A, B, D)
            flatTop(B, D, C)

    def glDrawPrimitives(self, vertices, stride):
        if self.primitiveType == POINTS:
            for i in range(0, len(vertices), stride):
                self.glPoint(*vertices[i:i+2], self.currColor)
        elif self.primitiveType == LINES:
            for i in range(0, len(vertices), stride * 2):
                self.glLine(vertices[i:i+2], vertices[i + stride:i + stride + 2], self.currColor)
        elif self.primitiveType == TRIANGLES:
            for i in range(0, len(vertices), stride * 3):
                A, B, C = vertices[i:i+stride], vertices[i + stride:i + stride + stride], vertices[i + stride * 2:i + stride * 2 + stride]
                self.glTriangle(A, B, C)

    def glDrawTrianglePoint(self, vA, vB, vC, vP):
        w, v, u = barycentricCoords([vA[0], vA[1]], [vB[0], vB[1]], [vC[0], vC[1]], [vP[0], vP[1]])
        if not (0 <= w <= 1 and 0 <= v <= 1 and 0 <= u <= 1):
            return
        z = w * vA[2] + v * vB[2] + u * vC[2]
        if not (self.vpX <= vP[0] < self.vpX + self.vpWidth and self.vpY <= vP[1] < self.vpY + self.vpHeight):
            return
        if z < self.zbuffer[vP[0]][vP[1]] and -1 <= z <= 1:
            self.zbuffer[vP[0]][vP[1]] = z
            if self.fragmentShader:
                color = self.fragmentShader(
                    verts=(vA, vB, vC),
                    bCoords=(w, v, u),
                    texture=self.activeTexture
                )
                self.glPoint(vP[0], vP[1], color)
            else:
                self.glPoint(vP[0], vP[1])

    def glLoadModel(self, model, texture=None, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        self.models.append(model)
        model.texture = texture
        model.Translate(*translate)
        model.Scale(*scale)
        model.Rotate(*rotate)

    def glLookAt(self, eye, camPos=(0, 0, 0)):
        self.camera.position[:3] = eye
        self.camera.target[:3] = camPos

    def glTransform(self, vertex, matrix):
        transformedVertex = matrix_mult(matrix, vertex)
        return [coord / transformedVertex[3] for coord in transformedVertex]

    def glShader(self, vertexShader=None, fragmentShader=None):
        self.vertexShader = vertexShader
        self.fragmentShader = fragmentShader
