import math
from tokenize import Single
import PySide6
from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QGraphicsSceneMouseEvent
from PySide6.QtGui import QWheelEvent, QDragMoveEvent, QMouseEvent
from PySide6.QtGui import QPen, QPainter, QColor, QBrush, QImage, QPixmap, qRgba
from PySide6.QtCore import QPoint, QPointF, QSize, Qt
from math import sqrt, pi, cos, sin
import numpy as np

class Singleton(object):
  _instance = None
  def __new__(class_, *args, **kwargs):
    if not isinstance(class_._instance, class_):
        class_._instance = object.__new__(class_, *args, **kwargs)
    return class_._instance

class Tile(QtWidgets.QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.grid = None
    def set_color(self, color:QColor):
        self.setPen(QPen(Qt.white))
        self.setBrush(QBrush(color))

class Terrain(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, width, height):
        super().__init__()
        self.grid = None
        self.width = width
        self.height = height

    def load_map_data(self):
        self.grid = np.random.rand(self.width, self.height) * 256
        self.width = 256
        self.height = 256
        self.grid_map = [[0 for x in range(self.width)] for y in range(self.height)] 
    
    def generate_tiles(self):
        rect_width = 10
        rect_height = 10
        for x in range(self.width):
            for y in range(self.height):
                tile = Tile()        
                tile.setRect(x*rect_width, y*rect_height, rect_width, rect_height)
                self.grid_map[x][y] = tile
                tile.set_color(QColor(self.grid[x][y]))
                self.scene().addItem(tile)

    def paint(self, painter: PySide6.QtGui.QPainter, option: PySide6.QtWidgets.QStyleOptionGraphicsItem, widget: PySide6.QtWidgets.QWidget) -> None:
        print("Paint")
        
        return super().paint(painter, option, widget)
        

class Player(QtWidgets.QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        
        self.setRect(0, 0, 10, 10)
        self.setBrush(Qt.red)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        print("clicked!")        
        return super().mousePressEvent(event)


class Camera(QtWidgets.QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        
        self.start_pos = None
        
    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Zoom in or out of the view.
        """
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        pos_x = event.position().x()
        pos_y =  event.position().y()
        oldPos = self.mapToScene(pos_x, pos_y)

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor

        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(pos_x, pos_y)

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
        return
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() is Qt.MouseButton.RightButton:
            self.start_pos = event.position()
        return
    
    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        self.start_pos = None
        return

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.start_pos is not None:
            # compute the difference between the current cursor position and the
            # previous saved origin point
            delta = self.start_pos - event.position()
            # get the current transformation (which is a matrix that includes the
            # scaling ratios
            transform = self.transform()
            # m11 refers to the horizontal scale, m22 to the vertical scale;
            # divide the delta by their corresponding ratio
            deltaX = delta.x() / transform.m11()
            deltaY = delta.y() / transform.m22()
            # translate the current sceneRect by the delta
            self.setSceneRect(self.sceneRect().translated(deltaX, deltaY))
            # update the new origin point to the current position
            self.start_pos = event.position()
        else:
            super(QtWidgets.QGraphicsView, self).mouseMoveEvent(event)

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        screen_width = 1024
        screen_height = 768
        self.scene = QtWidgets.QGraphicsScene(0, 0, screen_width, screen_height)

        terrain_width = 256
        terrain_height = 256
        terrain = Terrain(terrain_width, terrain_height)
        terrain.load_map_data()
        self.scene.addItem(terrain)
        terrain.generate_tiles()
        
        self.mainView = Camera(self.scene)
        self.mainView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mainView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.mainView.setFixedSize(screen_width, screen_height)
        self.mainView.viewport().setMouseTracking(True)

        self.setCentralWidget(self.mainView)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())