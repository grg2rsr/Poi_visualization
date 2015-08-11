# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import scipy as sp

""" code that runs a 3d animation of pois """

### pyqtgraph setup
app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 5
w.show()
w.setWindowTitle('Poi Pattern Visualization')

g = gl.GLGridItem()
w.addItem(g)

### Flags
show_left = True
show_right = True

### time
tsteps = 100
tvec = sp.linspace(0,2*sp.pi,tsteps)

### geometry setup
shoulder_width = 0.4
string_length = 1
arm_length = 1

# offset to ground level plane, but center of view rotation doesn't change
# so it kind of sucks ... either find a way to move grid, or to reposition
# center of view
offset = 0
offset_mat = sp.repeat([[0,0,offset]],tvec.shape[0],0)

### pattern definition
""" a pattern is defined in the following: (A,w,phi) for three tuples, each 
containing the tuple for the oscillation of (poi, hand, along y center) """
#
#pattern_left = sp.array([[1,1,0],[0.5,1,sp.pi],[0,0,0]])
#pattern_right = sp.array([[1,3,-sp.pi],[1,-1,0],[0.5,1,0]])

## antispin 4 petal flower
#pattern_left = sp.array([[1,3,0],[1,-1,0],[0,1,0]])
#pattern_right = sp.array([[1,3,0],[1,-1,-sp.pi],[0,1,0]])

## antispin 4 petal flower
pattern_left = sp.array([[1,3,0],[1,-1,0],[0,1,0]])
pattern_right = sp.array([[1,-3,0],[1,-1,0],[0,1,0]])

#t,xyz,phy,lr
Pos = sp.zeros((tsteps,3,3,2))

## left
poi_left_x_tmp = pattern_left[0,0] * sp.sin(pattern_left[0,1] * tvec + pattern_left[0,2])
poi_left_y_tmp = sp.zeros(tvec.shape[0])
poi_left_z_tmp = pattern_left[0,0] * sp.cos(pattern_left[0,1] * tvec+ pattern_left[0,2])

hand_left_x = pattern_left[1,0] * sp.sin(pattern_left[1,1]*tvec+pattern_left[1,2])
hand_left_y = pattern_left[2,0] * sp.sin(pattern_left[2,1]*tvec+pattern_left[2,2])
hand_left_z = pattern_left[1,0] * sp.cos(pattern_left[1,1]*tvec+pattern_left[1,2])

poi_left_x = hand_left_x + poi_left_x_tmp
poi_left_y = hand_left_y + poi_left_y_tmp
poi_left_z = hand_left_z + poi_left_z_tmp

hand_left_pos = sp.vstack((hand_left_x,hand_left_y,hand_left_z)).T + offset_mat
poi_left_pos = sp.vstack((poi_left_x,poi_left_y,poi_left_z)).T + offset_mat

## right
poi_right_x_tmp = pattern_right[0,0] * sp.sin(pattern_right[0,1] * tvec + pattern_right[0,2])
poi_right_y_tmp = sp.zeros(tvec.shape[0])
poi_right_z_tmp = pattern_right[0,0] * sp.cos(pattern_right[0,1] * tvec+ pattern_right[0,2])

hand_right_x = pattern_right[1,0] * sp.sin(pattern_right[1,1]*tvec+pattern_right[1,2])
hand_right_y = pattern_right[2,0] * sp.sin(pattern_right[2,1]*tvec+pattern_right[2,2])
hand_right_z = pattern_right[1,0] * sp.cos(pattern_right[1,1]*tvec+pattern_right[1,2])

poi_right_x = hand_right_x + poi_right_x_tmp
poi_right_y = hand_right_y + poi_right_y_tmp
poi_right_z = hand_right_z + poi_right_z_tmp

hand_right_pos = sp.vstack((hand_right_x,hand_right_y,hand_right_z)).T + offset_mat
poi_right_pos = sp.vstack((poi_right_x,poi_right_y,poi_right_z)).T + offset_mat

### colors
poi_left_col = (0.2,1,0.5,0.9)
hand_left_col = (0.2,0.5,1,0.9)

hand_right_col = (1,0.5,0.2,0.9)
poi_right_col = (1,0.2,0.5,0.9)

### visualization
## left
#left_side = {}
#left_side['hands']
#left_side['strings']
#left_side['pois']
#left_side['hand_trace']
#left_side['poi_trace']

poi_left_line = gl.GLLinePlotItem(pos=poi_left_pos,color=poi_left_col)
hand_left_line = gl.GLLinePlotItem(pos=hand_left_pos,color=hand_left_col)
poi_left_scatter = gl.GLScatterPlotItem(pos=poi_left_pos,color=poi_left_col,size=0.2,pxMode=False)
hand_left_scatter = gl.GLScatterPlotItem(pos=hand_left_pos,color=hand_left_col,size=0.1,pxMode=False)
string_left_line = gl.GLLinePlotItem(pos=sp.vstack((hand_left_pos[0],poi_left_pos[0])),color=poi_left_col,width=2)
#arm_left = gl.GLLinePlotItem(pos=sp.vstack((hand_left_pos[0],[0,-shoulder_width/2,0])),color=poi_left_col,width=2)
arm_left = gl.GLLinePlotItem(pos=sp.vstack((hand_left_pos[0],[0,0,offset])),color=poi_left_col,width=2)

w.addItem(poi_left_line)
w.addItem(poi_left_scatter)
w.addItem(hand_left_line)
w.addItem(hand_left_scatter)
w.addItem(arm_left)
w.addItem(string_left_line)

## right
poi_right_line = gl.GLLinePlotItem(pos=poi_right_pos,color=poi_right_col)
hand_right_line = gl.GLLinePlotItem(pos=hand_right_pos,color=hand_right_col)
poi_right_scatter = gl.GLScatterPlotItem(pos=poi_right_pos,color=poi_right_col,size=0.2,pxMode=False)
hand_right_scatter = gl.GLScatterPlotItem(pos=hand_right_pos,color=hand_right_col,size=0.1,pxMode=False)
string_right_line = gl.GLLinePlotItem(pos=sp.vstack((hand_right_pos[0],poi_right_pos[0])),color=poi_right_col,width=2)
#arm_right = gl.GLLinePlotItem(pos=sp.vstack((hand_right_pos[0],[0,shoulder_width/2,0])),color=poi_right_col,width=2)
arm_right = gl.GLLinePlotItem(pos=sp.vstack((hand_right_pos[0],[0,0,offset])),color=poi_right_col,width=2)

w.addItem(poi_right_line)
w.addItem(poi_right_scatter)
w.addItem(hand_right_line)
w.addItem(hand_right_scatter)
w.addItem(arm_right)
w.addItem(string_right_line)

#w.setCameraPosition(elevation=3*offset,distance=10)

### Animation
i = 0
def update():
    global i
    if i == tvec.shape[0]-1:
        i = 0
    else:
        i = i + 1
    
    if show_left:
        poi_left_scatter.setData(pos=sp.expand_dims(poi_left_pos[i],0))
        hand_left_scatter.setData(pos=sp.expand_dims(hand_left_pos[i],0))
        string_left_line.setData(pos=sp.vstack((hand_left_pos[i],poi_left_pos[i])))
#        arm_left.setData(pos=sp.vstack((hand_left_pos[i],[0,-1*shoulder_width/2,0])))
        arm_left.setData(pos=sp.vstack((hand_left_pos[i],[0,0,offset])))
    else:
        poi_left_scatter.hide()
        poi_left_line.hide()
        hand_left_scatter.hide()
        hand_left_line.hide()
        string_left_line.hide()
        arm_left.hide()
    
    if show_right:
        poi_right_scatter.setData(pos=sp.expand_dims(poi_right_pos[i],0))
        hand_right_scatter.setData(pos=sp.expand_dims(hand_right_pos[i],0))
        string_right_line.setData(pos=sp.vstack((hand_right_pos[i],poi_right_pos[i])))
#        arm_right.setData(pos=sp.vstack((hand_right_pos[i],[0,shoulder_width/2,0])))
        arm_right.setData(pos=sp.vstack((hand_right_pos[i],[0,0,offset])))
    else:
        poi_right_scatter.hide()
        poi_right_line.hide()
        hand_right_scatter.hide()
        hand_right_line.hide()
        string_right_line.hide()
        arm_right.hide()
    
t = QtCore.QTimer()
t.timeout.connect(update)
t.start(50)


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
