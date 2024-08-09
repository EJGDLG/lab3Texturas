from MathLib import matrix_mult

def vertexShader(vertex, **kwargs):
    modelMatrix = kwargs["modelMatrix"]
    viewMatrix = kwargs["viewMatrix"]
    projectionMatrix = kwargs["projectionMatrix"]
    viewportMatrix = kwargs["viewportMatrix"]
    
    vt = [vertex[0], vertex[1], vertex[2], 1]
    vt = matrix_mult(viewportMatrix, matrix_mult(projectionMatrix, matrix_mult(viewMatrix, matrix_mult(modelMatrix, vt))))
    vt = [vt[0] / vt[3], vt[1] / vt[3], vt[2] / vt[3]]
    
    return vt

def fragmentShader(**kwargs):
    A, B, C = kwargs["verts"]
    u, v, w = kwargs["bCoords"]
    texture = kwargs["texture"]

    # Verificar que cada vértice tenga al menos 5 componentes
    if len(A) < 5 or len(B) < 5 or len(C) < 5:
        raise ValueError("Cada vértice debe tener al menos 5 componentes")

    # Coordenadas de textura
    vtA = [A[3], A[4]]
    vtB = [B[3], B[4]]
    vtC = [C[3], C[4]]

    # Inicializar el color base
    r = 1
    g = 1
    b = 1

    # Calcular las coordenadas de textura interpoladas
    vtP = [
        u * vtA[0] + v * vtB[0] + w * vtC[0],
        u * vtA[1] + v * vtB[1] + w * vtC[1]
    ]

    # Verificar si la textura está disponible
    if texture:
        # Asegurarse de que las coordenadas de textura estén dentro del rango válido
        if 0 <= vtP[0] < texture.width and 0 <= vtP[1] < texture.height:
            texColor = texture.getColor(vtP[0], vtP[1])
            r *= texColor[0]
            g *= texColor[1]
            b *= texColor[2]
        else:
            # Si las coordenadas de textura están fuera del rango, usar el color base
            print(f"Advertencia: Coordenadas de textura fuera del rango: {vtP}")

    return [r, g, b]
