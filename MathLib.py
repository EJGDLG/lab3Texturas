from math import pi, sin, cos

def barycentricCoords(A, B, C, P):
    # Asumimos que A, B, C y P son tuplas (x, y)
    # Devuelve las coordenadas baricéntricas (w, v, u)
    
    # Cálculo del área del triángulo
    def area(x1, y1, x2, y2, x3, y3):
        return abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2.0)
    
    area_ABC = area(A[0], A[1], B[0], B[1], C[0], C[1])
    area_PAB = area(P[0], P[1], A[0], A[1], B[0], B[1])
    area_PBC = area(P[0], P[1], B[0], B[1], C[0], C[1])
    area_PCA = area(P[0], P[1], C[0], C[1], A[0], A[1])
    
    # Coordenadas baricéntricas
    w = area_PBC / area_ABC
    v = area_PCA / area_ABC
    u = area_PAB / area_ABC
    
    return w, v, u

def matrix_mult(A, B):
    # Si B es una lista (vector), se multiplica por la matriz A
    if isinstance(B[0], list):
        # Multiplicación de matrices
        return [[sum(a * b for a, b in zip(A_row, B_col)) for B_col in zip(*B)] for A_row in A]
    else:
        # Multiplicación de matriz por vector
        return [sum(a * b for a, b in zip(A_row, B)) for A_row in A]


def TranslationMatrix(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ]

def RotationMatrix(rx, ry, rz):
    # Implementa las matrices de rotación aquí.
    # Ejemplo de rotación alrededor del eje Z
    import math
    return [
        [math.cos(rz), -math.sin(rz), 0, 0],
        [math.sin(rz), math.cos(rz), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

def ScaleMatrix(sx, sy, sz):
    return [
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ]


    # Matrices de rotación para cada eje
    pitchMat = [
        [1, 0, 0, 0],
        [0, cos(pitch), -sin(pitch), 0],
        [0, sin(pitch), cos(pitch), 0],
        [0, 0, 0, 1]
    ]

    yawMat = [
        [cos(yaw), 0, sin(yaw), 0],
        [0, 1, 0, 0],
        [-sin(yaw), 0, cos(yaw), 0],
        [0, 0, 0, 1]
    ]

    rollMat = [
        [cos(roll), -sin(roll), 0, 0],
        [sin(roll), cos(roll), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]
    
def matrix_inv(matrix):
    def submatrix(matrix, row, col):
        return [row[:col] + row[col+1:] for row in (matrix[:row] + matrix[row+1:])]

    def determinant(matrix):
        if len(matrix) == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        return sum(((-1) ** col) * matrix[0][col] * determinant(submatrix(matrix, 0, col)) for col in range(len(matrix)))

    def cofactor(matrix):
        return [[(-1) ** (row + col) * determinant(submatrix(matrix, row, col)) for col in range(len(matrix))] for row in range(len(matrix))]

    det = determinant(matrix)
    if det == 0:
        raise ValueError("La matriz es singular y no se puede invertir.")

    cof = cofactor(matrix)
    cof_transpose = list(map(list, zip(*cof)))
    return [[elem / det for elem in row] for row in cof_transpose]

    # Multiplicar las matrices de rotación (pitchMat * yawMat * rollMat)
    return matrix_mult(matrix_mult(pitchMat, yawMat), rollMat)
