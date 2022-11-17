from kivy.graphics import PushMatrix, Scale, Translate, PopMatrix, Mesh, Rectangle


def makePushMatrixInstruction():
    return PushMatrix


def makeScaleInstruction(x, y):
    x_ = float(x)
    y_ = float(y)
    return lambda: Scale(x_, y_, 0)


def makeTranslateInstruction(x, y):
    x_ = float(x)
    y_ = float(y)
    return lambda: Translate(x_, y_)


def makePopMatrixInstruction():
    return PopMatrix


def makeMeshInstruction(imageName, *points):
    points_ = []
    for point in points:
        points_.append(int(point))
    return lambda: Mesh(verticies=points_, indecies=[i for i in range(int(len(points_)/4))], source=imageName)


def makeImageInstruction(imageName, x, y, w, h):
    x_ = float(x)
    y_ = float(y)
    w_ = float(w)
    h_ = float(h)
    return lambda: Rectangle(pos=(x_, y_), size=(w_, h_), source=f"resources/notationSymbols/assets/{imageName}.png")

