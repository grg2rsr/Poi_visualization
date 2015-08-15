# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import scipy as sp
import sys
import time
""" code that runs a 3d animation of pois """

"""
now recode with GUI. Layout:

gui contains fields to set:

time:
number of timesteps = resolution
play speed

geometry:
pattern: (A,w,phi) for (poi,hand,along y center) # , shoulder) (implementing shoulder means, that hand position has to be recalc)
- pattern is a table
shoulder width
string length
arm length

visualization
colors
show flags (left, right, traces)
checkboxes

trace slider

communication:
on init, default pattern

on change of anything (patten, color, show flags)
call update


"""
#==============================================================================
# Main GUI
#==============================================================================
class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        ### default constants
        self.shoulder_width = 0.4
        self.string_length = 1
        self.arm_length = 1.2
        
        self.colors = {}
        self.colors['l'] = {'poi':          (0.2,0.9,0.5,0.9),
                            'string':       (0.2,0.9,0.5,0.9),
                            'hand':         (0.2,0.9,0.5,0.9),
                            'arm':          (0.2,0.9,0.5,0.9),
                            'poi_trace':    (0.2,0.9,0.5,0.9),
                            'hand_trace':   (0.2,0.9,0.5,0.9),
                            'frac_trace':   (0.2,0.9,0.5,0.9)}
                            
        self.colors['r'] = {'poi':          (1.0,0.2,0.5,0.9),
                            'string':       (1.0,0.2,0.5,0.9),
                            'hand':         (1.0,0.2,0.5,0.9),
                            'arm':          (1.0,0.2,0.5,0.9),
                            'poi_trace':    (1.0,0.2,0.5,0.9),
                            'hand_trace':   (1.0,0.2,0.5,0.9),
                            'frac_trace':   (1.0,0.2,0.5,0.9)}

        self.init_timing()
        self.init_pattern()
        self.init_UI()
                
    def init_pattern(self,Pattern=None):
        # receives pattern from UI, calculates the new position matrix
        """ a pattern is defined as
        (A,w,phi)
        
        for three (four) tuples
        
        (poi, hand, along y center) (and shoulder) """
        
        if Pattern == None:
            # ini with default pattern: antispin 4 petal flower
            pattern_left  = sp.array([[ self.string_length, 3, 0], [ self.arm_length,-1, 0], [ 0, 1, 0]])
            pattern_right = sp.array([[ self.string_length,-3, 0], [ self.arm_length, 1, 0], [ 0, 1, 0]])
            Pattern = sp.concatenate((pattern_right[:,:,sp.newaxis],pattern_left[:,:,sp.newaxis]),axis=2)
        
        """
        variable naming definitions: full array that holds all position coordinates is 
        called Pos
        poi_p denotes poi position in it's own coordinate space (0,0,0) is the pos of the
        hand
        poi denotes the total poi position (poi + hand)
        """
        
        """ definitino of multidim pos array 
        dims are: t,x y z,pp p h s, r l
        t : time
        x y z : coordinates
        pp : pos of poi in own coordinate space
        p : pos of poi in normal coordinate space
        h : pos of hand
        s : pos of shoulder
        r l : right, left
        """

        Pos = sp.zeros((self.tSteps,3,4,2))
        
        Pos[:,0,[0,2,3],:] = Pattern[:,0,:] * sp.sin(Pattern[:,1,:] * self.tvec[:,sp.newaxis,sp.newaxis] + Pattern[:,2,:])
        Pos[:,2,[0,2,3],:] = Pattern[:,0,:] * sp.cos(Pattern[:,1,:] * self.tvec[:,sp.newaxis,sp.newaxis] + Pattern[:,2,:])
        # Pos[:,1,:,0] # y axis is unset, no 3d movement so far
        
        Pos[:,:,1,:] = Pos[:,:,0,:] + Pos[:,:,2,:] # adding poi position
        
        # adding shoulder width
        Pos[:,1,:,0] -= self.shoulder_width/2
        Pos[:,1,:,1] += self.shoulder_width/2

        self.Pattern = Pattern
        self.Pos = Pos
    
    def init_timing(self,tSteps=100):
        """ sets up the QtTimer and time vector. Maybe have a separate function
        that is called when time steps change"""
        self.tSteps = tSteps
        self.tvec = sp.linspace(0,2*sp.pi,self.tSteps)
        self.t = self.tvec[0]
        
        self.QtTimer = QtCore.QTimer()
        self.QtTimer.timeout.connect(self.loop)
    
    def update_GLitems(self):
        
        ### moveable
        ### pois
        self.poi_right.PosMat = self.Pos[:,:,1,0]
        self.poi_right.setData(pos=self.Pos[0,:,1,0][sp.newaxis,:], color=self.colors['r']['poi'],size=0.2,pxMode=False)
        
        self.poi_left.PosMat = self.Pos[:,:,1,1]
        self.poi_left.setData(pos=self.Pos[0,:,1,1][sp.newaxis,:], color=self.colors['l']['poi'],size=0.2,pxMode=False)
        
        ### strings
        self.poi_right_string_data = sp.concatenate((self.Pos[:,:,1,0,sp.newaxis],self.Pos[:,:,2,0,sp.newaxis]),axis=2)
        self.poi_left_string_data =  sp.concatenate((self.Pos[:,:,1,1,sp.newaxis],self.Pos[:,:,2,1,sp.newaxis]),axis=2)
        
        self.poi_right_string.PosMat = self.poi_right_string_data
        self.poi_right_string.setData(pos=self.poi_right_string_data[0].T,color=self.colors['r']['string'])
        
        self.poi_left_string.PosMat = self.poi_left_string_data
        self.poi_left_string.setData(pos=self.poi_left_string_data[1].T,color=self.colors['l']['string'])
        
        ### hands
        self.hand_right.PosMat = self.Pos[:,:,2,0]
        self.hand_right.setData(pos=self.Pos[0,:,2,0][sp.newaxis,:], color=self.colors['r']['hand'],size=0.1,pxMode=False)
        
        self.hand_left.PosMat = self.Pos[:,:,2,1]
        self.hand_left.setData(pos=self.Pos[0,:,2,1][sp.newaxis,:], color=self.colors['l']['hand'],size=0.1,pxMode=False)
        
        ### arms
        self.arm_left_data =  sp.concatenate((self.Pos[:,:,2,1,sp.newaxis],self.Pos[:,:,3,1,sp.newaxis]),axis=2)
        self.arm_right_data = sp.concatenate((self.Pos[:,:,2,0,sp.newaxis],self.Pos[:,:,3,0,sp.newaxis]),axis=2)
        
        self.arm_left.PosMat = self.arm_left_data
        self.arm_left.setData(pos=self.arm_left_data[1].T,color=self.colors['l']['arm'],width=2)
        
        self.arm_right .PosMat = self.arm_right_data
        self.arm_right.setData(pos=self.arm_right_data[0].T,color=self.colors['r']['arm'],width=2)
        
        
        ### static traces
        self.poi_left_trace.setData(pos=self.Pos[:,:,1,1],color=self.colors['l']['poi_trace'])
        self.poi_right_trace.setData(pos=self.Pos[:,:,1,0],color=self.colors['r']['poi_trace'])
        
        self.hand_left_trace.setData(pos=self.Pos[:,:,2,1],color=self.colors['l']['hand_trace'])
        self.hand_right_trace.setData(pos=self.Pos[:,:,2,0],color=self.colors['r']['hand_trace']) 
        
    def init_UI(self):
        """ initializes UI"""        
        
        ### Setting up Graphical Display Widget
        self.Display = gl.GLViewWidget()
        self.Display.opts['distance'] = 6
        
        self.poi_right = myGLScatter()
        self.poi_left =  myGLScatter()
        
        self.poi_right_string = myGLLine()
        self.poi_left_string  = myGLLine()
        
        self.hand_right = myGLScatter()
        self.hand_left =  myGLScatter()
        
        self.arm_left  = myGLLine()
        self.arm_right = myGLLine()
        
        self.poi_right_trace = gl.GLLinePlotItem()
        self.poi_left_trace =  gl.GLLinePlotItem()
        
        self.hand_left_trace =  gl.GLLinePlotItem()
        self.hand_right_trace = gl.GLLinePlotItem()
        
        self.update_list = [self.poi_right,self.poi_left,self.poi_left_string,self.poi_right_string,self.arm_left,self.arm_right,self.hand_right,self.hand_left]

        self.update_GLitems()
        
        grid = gl.GLGridItem()
        self.Display.addItem(grid)
        self.Display.addItem(self.poi_left_string)
        self.Display.addItem(self.poi_right_string)
        self.Display.addItem(self.poi_left)
        self.Display.addItem(self.poi_right)
        self.Display.addItem(self.hand_left)
        self.Display.addItem(self.hand_right)
        self.Display.addItem(self.arm_left)
        self.Display.addItem(self.arm_right)
        self.Display.addItem(self.poi_left_trace)
        self.Display.addItem(self.poi_right_trace)
        self.Display.addItem(self.hand_left_trace)
        self.Display.addItem(self.hand_right_trace)
        
        ### Setting up Control Panel Widget
        self.Control = ControlWidget(Main=self)
        
        ### Full Window with QSplitter layout
        self.Splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.Splitter.addWidget(self.Display)
        self.Splitter.addWidget(self.Control)
        self.setCentralWidget(self.Splitter)
        
        # resizing splitter
        # note: http://stackoverflow.com/questions/16280323/qt-set-size-of-qmainwindow
        frac = 0.8
        self.Splitter.setSizes([int(self.Splitter.size().height() * frac), int(self.Splitter.size().height() * (1-frac))])
        
        self.setGeometry(200, 200, 850, 600)
        self.setWindowTitle('Poi Visualization')              
        self.show()
        
        ### Fixme move this to a seperate function
        self.QtTimer.start(50) # 50 ms = 20 Hz. Not super smooth, maybe check for a better solution
        
    def loop(self):
        ### FIXME needs to be called w fixed time base
        if self.t == self.tvec.shape[0]-1: 
            self.t = 0
        else:
            self.t = self.t + 1
        
        for item in self.update_list:
            item.update_(self.t)
        
    def time_base_change(self):
        """ called upon tSteps change """
        pass

        
#==============================================================================
# subclasses
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
    def __init__(self,PosMat=None,side='right',**kwargs):
        gl.GLScatterPlotItem.__init__(self,**kwargs)
        self.side = side
        self.PosMat = PosMat # tvec.shape[0] x 3

    
    def update_(self,i):
        """ updates position based on i """
        self.setData(pos=self.PosMat[i,:][sp.newaxis,:])

#==============================================================================
# Widgets        
#==============================================================================
class ControlWidget(QtGui.QWidget):

    def __init__(self,Main=None,*args,**kwargs):
        QtGui.QWidget.__init__(self,*args,**kwargs)
        
        self.Main = Main
        self.col = (0,0,0,0)
        self.initUI()
        
    def initUI(self):
        self.layout = QtGui.QGridLayout()
        
        # top row labels
        self.layout.addWidget(QtGui.QLabel('left'),0,1)
        self.layout.addWidget(QtGui.QLabel('right'),0,2)

        # create spinboxes for poi, arm
        self.Poi_w = [QtGui.QDoubleSpinBox(self),QtGui.QDoubleSpinBox(self)]
        self.Poi_p = [QtGui.QDoubleSpinBox(self),QtGui.QDoubleSpinBox(self)]
        
        self.Hand_w = [QtGui.QDoubleSpinBox(self),QtGui.QDoubleSpinBox(self)]        
        self.Hand_p = [QtGui.QDoubleSpinBox(self),QtGui.QDoubleSpinBox(self)]        

        # set initial values        
        # extend range before value set
        for SpinBox in self.Poi_w + self.Poi_p + self.Hand_w + self.Hand_p:
            SpinBox.setRange(-100.0,100.0)
            
        [self.Poi_w[i].setValue(self.Main.Pattern[0,1,i]) for i in range(2)]
        [self.Poi_p[i].setValue(self.Main.Pattern[0,2,i]) for i in range(2)]
        [self.Hand_w[i].setValue(self.Main.Pattern[1,1,i]) for i in range(2)]
        [self.Hand_p[i].setValue(self.Main.Pattern[1,2,i]) for i in range(2)]
        
        # add to layout
        self.layout.addWidget(QtGui.QLabel('Poi w'),1,0)
        [self.layout.addWidget(self.Poi_w[i],1,i+1) for i in range(2)]
        
        self.layout.addWidget(QtGui.QLabel('Poi phase'),2,0)
        [self.layout.addWidget(self.Poi_p[i],2,i+1) for i in range(2)]

        self.layout.addWidget(QtGui.QLabel('Arm w'),3,0)
        [self.layout.addWidget(self.Hand_w[i],3,i+1) for i in range(2)]

        self.layout.addWidget(QtGui.QLabel('Arm phase'),4,0)
        [self.layout.addWidget(self.Hand_p[i],4,i+1) for i in range(2)]

        # connect        
        for SpinBox in self.Poi_w + self.Poi_p + self.Hand_w + self.Hand_p:
            SpinBox.valueChanged.connect(self.pattern_change)
            
        for SpinBox in self.Poi_p + self.Hand_p:
            SpinBox.setSingleStep(sp.pi/2)
            
#        self.btn = QtGui.QPushButton('color selector widget', self)
#        self.btn.clicked.connect(self.getColor)

        self.setLayout(self.layout)
        self.show()
        
    def pattern_change(self,value):
        
        pattern_right = sp.array([[ self.Main.string_length, self.Poi_w[0].value(), self.Poi_p[0].value()], [ self.Main.arm_length, self.Hand_w[0].value(), self.Hand_p[0].value()], [ 0, 1, 0]])
        pattern_left  = sp.array([[ self.Main.string_length, self.Poi_w[1].value(), self.Poi_p[1].value()], [ self.Main.arm_length, self.Hand_w[1].value(), self.Hand_p[1].value()], [ 0, 1, 0]])
        
        Pattern = sp.concatenate((pattern_right[:,:,sp.newaxis],pattern_left[:,:,sp.newaxis]),axis=2)
        
        self.Main.init_pattern(Pattern)
        self.Main.update_GLitems()
        
        
    def getColor(self):
      
        col = QtGui.QColorDialog.getColor()
        self.col = col

#==============================================================================
# main
#==============================================================================

def main():
    app = QtGui.QApplication(sys.argv)
    W = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



#==============================================================================
# some leftovers, patterns ...
#==============================================================================
        # 4 petal and isolation
        #pattern_left = sp.array([[1,1,0],[0.5,1,sp.pi],[0,0,0]])
        #pattern_right = sp.array([[1,3,-sp.pi],[1,-1,0],[0.5,1,0]])
        
        ## something else weird - same spin 4 petal flower
        #pattern_left = sp.array([[1,3,0],[1,-1,0],[0,1,0]])
        #pattern_right = sp.array([[1,3,0],[1,-1,-sp.pi],[0,1,0]])
        
        ## something else pretty nice
#        pattern_left  = sp.array([[ 1,-3, 0], [ 1,-1, 0], [ 0, 1, 0]])
#        pattern_right = sp.array([[ 1, 3, 0], [ 1, 1, 0], [ 0, 1, 0]])
        
        ## something weird - same spin with arms physically impossible though
        #pattern_left  = sp.array([[ 1, 3, 0], [ 1,-1, 0], [ 0, 1, 0]])
        #pattern_right = sp.array([[ 1,-3, 0], [ 1,-1, 0], [ 0, 1, 0]])