# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import scipy as sp

""" code that runs a 3d animation of pois """

#==============================================================================
#  pyqtgraph and vis setup
#==============================================================================
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

#==============================================================================
#  geometry setup
#==============================================================================

### time
tsteps = 100
tvec = sp.linspace(0,2*sp.pi,tsteps)

### constants
shoulder_width = 0.4
string_length = 1.2
arm_length = 1

# offset to ground level plane, but center of view rotation doesn't change
# so it kind of sucks ... either find a way to move grid, or to reposition
# center of view
offset = 0
offset_mat = sp.repeat([[0,0,offset]],tvec.shape[0],0)

""" a pattern is defined in the following: (A,w,phi) for three tuples, each 
containing the tuple for the oscillation of (poi, hand, along y center) 

variable naming definitions: full array that holds all position coordinates is 
called Pos
poi_p denotes poi position in it's own coordinate space (0,0,0) is the pos of the
hand
poi denotes the total poi position (poi + hand)
"""

# 4 petal and isolation
#pattern_left = sp.array([[1,1,0],[0.5,1,sp.pi],[0,0,0]])
#pattern_right = sp.array([[1,3,-sp.pi],[1,-1,0],[0.5,1,0]])

## something else weird - same spin 4 petal flower
#pattern_left = sp.array([[1,3,0],[1,-1,0],[0,1,0]])
#pattern_right = sp.array([[1,3,0],[1,-1,-sp.pi],[0,1,0]])

## something else pretty nice
#pattern_left  = sp.array([[ 1,-3, 0], [ 1,-1, 0], [ 0, 1, 0]])
#pattern_right = sp.array([[ 1, 3, 0], [ 1, 1, 0], [ 0, 1, 0]])

## something weird
#pattern_left  = sp.array([[ 1, 3, 0], [ 1,-1, 0], [ 0, 1, 0]])
#pattern_right = sp.array([[ 1,-3, 0], [ 1,-1, 0], [ 0, 1, 0]])

## classic antispin flower
pattern_left  = sp.array([[ string_length, 3, 0], [ arm_length,-1, 0], [ 0, 1, 0]])
pattern_right = sp.array([[ string_length,-3, 0], [ arm_length, 1, 0], [ 0, 1, 0]])

Pattern = sp.concatenate((pattern_left[:,:,sp.newaxis],pattern_right[:,:,sp.newaxis]),axis=2)

""" definitino of multidim pos array 
dims are: t,x y z,pp p h y, r l
t : time
x y z : coordinates
pp : pos of poi in own coordinate space
p : pos of poi in normal coordinate space
h : pos of hand
r l : right, left
"""

Pos = sp.zeros((tsteps,3,4,2))

Pos[:,0,[0,2,3],:] = Pattern[:,0,:] * sp.sin(Pattern[:,1,:] * tvec[:,sp.newaxis,sp.newaxis] + Pattern[:,2,:])
Pos[:,2,[0,2,3],:] = Pattern[:,0,:] * sp.cos(Pattern[:,1,:] * tvec[:,sp.newaxis,sp.newaxis] + Pattern[:,2,:])
# Pos[:,1,:,0] # y axis is unset, no 3d movement so far

Pos[:,:,1,:] = Pos[:,:,0,:] + Pos[:,:,2,:] # adding poi position

# adding shoulder width
Pos[:,1,:,0] -= shoulder_width/2
Pos[:,1,:,1] += shoulder_width/2




#==============================================================================
# visualization setup
#==============================================================================

class myGLLine(gl.GLLinePlotItem):
    """ subclassing GLLine """
    def __init__(self,PosMat=None,side='right',**kwargs):
        gl.GLLinePlotItem.__init__(self,**kwargs)
        self.side = side
        self.PosMat = PosMat # tvec.shape[0] x 3 x 2 , last dimension is the fixed point
    
    def update_(self,i):
        """ updates position based on i """
        self.setData(pos=self.PosMat[i,:,:].T) # receices 2 x 3 as from, to
    
    
class myGLScatter(gl.GLScatterPlotItem):
    """ subclassing GLScatter """
    def __init__(self,pos,side='right',**kwargs):
        gl.GLScatterPlotItem.__init__(self,**kwargs)
        self.side = side
        self.pos = pos # tvec.shape[0] x 3
#        self.update_(0)
    
    def update_(self,i):
        """ updates position based on i """
        self.setData(self.pos[i,:])
        
#poi_left_scatter = gl.GLScatterPlotItem(pos=poi_left_pos,color=poi_left_col,size=0.2,pxMode=False)


""" also cool idea to implement: a slider that sets the trace position from a 
fraction of the string length """


""" rename variables:
poi, hand, trace, line"""
### colors
poi_left_col = (0.2,1,0.5,0.9) # replace by color from qt based color picking widget
hand_left_col = (0.2,0.5,1,0.9)

hand_right_col = (1,0.5,0.2,0.9)
poi_right_col = (1,0.2,0.5,0.9)


### taking the pos back out of the array, just for checking, will be replaced alter
poi_left_pos = Pos[:,:,1,1]
hand_left_pos = Pos[:,:,2,1]

poi_right_pos = Pos[:,:,1,0]
hand_right_pos = Pos[:,:,2,0]

data_left = sp.concatenate((Pos[:,:,1,1,sp.newaxis],Pos[:,:,2,1,sp.newaxis]),axis=2)
data_right = sp.concatenate((Pos[:,:,1,0,sp.newaxis],Pos[:,:,2,0,sp.newaxis]),axis=2)

poi_left_string = myGLLine(PosMat = data_left,pos=data_left[1].T,color=poi_left_col)
poi_right_string = myGLLine(PosMat = data_right,pos=data_left[0].T,color=poi_right_col)

#poi_left_line = gl.GLLinePlotItem(pos=poi_left_pos,color=poi_left_col)
#hand_left_line = gl.GLLinePlotItem(pos=hand_left_pos,color=hand_left_col)

poi_left_scatter = gl.GLScatterPlotItem(pos=poi_left_pos,color=poi_left_col,size=0.2,pxMode=False)
hand_left_scatter = gl.GLScatterPlotItem(pos=hand_left_pos,color=hand_left_col,size=0.1,pxMode=False)

string_left_line = gl.GLLinePlotItem(pos=sp.vstack((hand_left_pos[0],poi_left_pos[0])),color=poi_left_col,width=2)
#arm_left = gl.GLLinePlotItem(pos=sp.vstack((hand_left_pos[0],[0,-shoulder_width/2,0])),color=poi_left_col,width=2)
arm_left = gl.GLLinePlotItem(pos=sp.vstack((hand_left_pos[0],[0,0,offset])),color=poi_left_col,width=2)

w.addItem(poi_left_string)
w.addItem(poi_right_string)
#w.addItem(poi_left_scatter)
#w.addItem(hand_left_line)
#w.addItem(hand_left_scatter)
#w.addItem(arm_left)
#w.addItem(string_left_line)

## right
#poi_right_line = gl.GLLinePlotItem(pos=poi_right_pos,color=poi_right_col)
#hand_right_line = gl.GLLinePlotItem(pos=hand_right_pos,color=hand_right_col)
#poi_right_scatter = gl.GLScatterPlotItem(pos=poi_right_pos,color=poi_right_col,size=0.2,pxMode=False)
#hand_right_scatter = gl.GLScatterPlotItem(pos=hand_right_pos,color=hand_right_col,size=0.1,pxMode=False)
#string_right_line = gl.GLLinePlotItem(pos=sp.vstack((hand_right_pos[0],poi_right_pos[0])),color=poi_right_col,width=2)
##arm_right = gl.GLLinePlotItem(pos=sp.vstack((hand_right_pos[0],[0,shoulder_width/2,0])),color=poi_right_col,width=2)
#arm_right = gl.GLLinePlotItem(pos=sp.vstack((hand_right_pos[0],[0,0,offset])),color=poi_right_col,width=2)
#
#w.addItem(poi_right_line)
#w.addItem(poi_right_scatter)
#w.addItem(hand_right_line)
#w.addItem(hand_right_scatter)
#w.addItem(arm_right)
#w.addItem(string_right_line)

#w.setCameraPosition(elevation=3*offset,distance=10)
items = w.items[1:]
#==============================================================================
# Animation run
#==============================================================================

i = 0
def update():
    global i # unclear why needed, seems Qt specific?
    
    # infinite looping through the tvec 
    if i == tvec.shape[0]-1: 
        i = 0
    else:
        i = i + 1
    
    """ idea for more general visualization that will work better with live 
    GUI interaction: iterate over all visible objects and call an update function
    each timestep. update will include new position and show/not show, color etc.
    maybe subclassing necessary"""
    for item in items:
        item.update_(i)
        
#    if show_left:
#        poi_left_scatter.setData(pos=sp.expand_dims(poi_left_pos[i],0))
#        hand_left_scatter.setData(pos=sp.expand_dims(hand_left_pos[i],0))
#        string_left_line.setData(pos=sp.vstack((hand_left_pos[i],poi_left_pos[i])))
##        arm_left.setData(pos=sp.vstack((hand_left_pos[i],[0,-1*shoulder_width/2,0])))
#        arm_left.setData(pos=sp.vstack((hand_left_pos[i],[0,0,offset])))
#    else:
#        poi_left_scatter.hide()
#        poi_left_line.hide()
#        hand_left_scatter.hide()
#        hand_left_line.hide()
#        string_left_line.hide()
#        arm_left.hide()
    
#    if show_right:
#        poi_right_scatter.setData(pos=sp.expand_dims(poi_right_pos[i],0))
#        hand_right_scatter.setData(pos=sp.expand_dims(hand_right_pos[i],0))
#        string_right_line.setData(pos=sp.vstack((hand_right_pos[i],poi_right_pos[i])))
##        arm_right.setData(pos=sp.vstack((hand_right_pos[i],[0,shoulder_width/2,0])))
#        arm_right.setData(pos=sp.vstack((hand_right_pos[i],[0,0,offset])))
#    else:
#        poi_right_scatter.hide()
#        poi_right_line.hide()
#        hand_right_scatter.hide()
#        hand_right_line.hide()
#        string_right_line.hide()
#        arm_right.hide()

""" replace with a OO structure, MainWindow etc. put pg Widget into a
Qt.MainWindow, next to it vis and pattern controls """

t = QtCore.QTimer()
t.timeout.connect(update)
t.start(50) # 50 ms = 20 Hz. Not super smooth, maybe check for a better solution


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
