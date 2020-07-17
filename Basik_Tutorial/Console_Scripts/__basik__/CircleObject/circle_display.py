
import numpy as np
import matplotlib.pyplot as plt

from ..utils import quarter_circle
from .circle import Circle


#------------------------------------------------------------------------------

class CircleDisplay(object):
    
    DISPLAY = True
    
    
    N_entrance0 = np.array([60,100])
    N_exit0 = np.array([40,100])
    N_halt0 = np.array([60,90])
    
    E_entrance0 = np.array([100,40])
    E_exit0 = np.array([100,60])
    E_halt0 = np.array([90,40])
    
    S_entrance0 = np.array([40,0])
    S_exit0 = np.array([60,0])
    S_halt0 = np.array([40,10])
    
    W_entrance0 = np.array([0,60])
    W_exit0 = np.array([0,40])
    W_halt0 = np.array([10,60])
    
    center0 = np.array([50,50])
    radius0 = 30
    
    extent0 = np.array([0,100,0,100])
    shrink = 0.9
    
    # Large
    large_standard_car_length = 5
    large_standard_car_width = 2.5
    
    # Medium
    medium_standard_car_length = 7
    medium_standard_car_width = 3.5
    
    # Small
    small_standard_car_length = 10
    small_standard_car_width = 5
    
    circle_image = plt.imread('__basik__/Images/circle_trees.jpg')
    
    #--------------------------------------------------------------------------

    
    def __init__(self,circle_object,
                      axes=None,
                      frames_per_move:int=3,
                      view_track:bool=False):
        
        '''
        Parameters:
        -----------
        circle_object: __basik__.CircleObject.circle.Circle
            The internal circle object that provides the mechanism for the
            simulation to follow. CircleDisplay object will display the progress 
            of this circle_object.  
        axes: matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes on which the display will be rendered. If set
            to None, one will be created along with self.figure.
        frames_per_move: int
            How many times a vehicle will render movement in an executed
            transition from one node to another.
        view_track: bool
            The circle_object consists of nodes between which vehicle from.
            These nodes can be visualised on the circle display. This was 
            originally intende for debugging purposes but has proved to be an
            interesting feature to include.
        '''
        
        self.size = circle_object.size
        
        self.axes = axes

        if self.size == 3:
            self.standard_car_length = self.small_standard_car_length
        elif self.size == 5:
            self.standard_car_length = self.medium_standard_car_length
        else:
            self.standard_car_length = self.large_standard_car_length
            
        assert isinstance(circle_object,Circle)
        self.circle_object = circle_object    
        
        self.frames_per_move = frames_per_move
        
        self.setup_image()
        self.scale_all()
        self.build_tracks()
        self.correct_entrances_and_exits()
        if view_track:
            self.view_track()
            
        self.turn_on_display()
        
    #--------------------------------------------------------------------------    
    
    def turn_on_display(self):
        
        for node in self.circle_object.entrances:
            node.circle_display = self
        
        track_idx = 0
        for quarter in self.circle_object.quarters:
            for node in quarter.nodes:
                node.circle_display = self
                node.circle_track_idx = track_idx
                track_idx += 1

        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):
        
        for node in self.circle_object.entrances:
            node.circle_display = None
            
        for quarter in self.circle_object.quarters:
            for node in quarter.nodes:
                node.circle_display = None
                node.circle_track_idx = None
            
        return None
    
    #--------------------------------------------------------------------------

    
    def setup_image(self,car_length=10,car_width=5):
        
        self.car_length = car_length
        self.car_width = car_width
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        self.axes.set_axis_off()
        
        self.image = self.circle_image
        
        assert self.shrink < 1
        
        self.scale_factor = self.car_length/(self.shrink*self.standard_car_length)
        self.extent = self.extent0*self.scale_factor
        self.xlim = self.extent[1]
        self.ylim = self.extent[3]
        
        self.show()
        
        return None
        
    #--------------------------------------------------------------------------
    
    def scale_all(self):
        
        
        self.N_entrance = self.N_entrance0*self.scale_factor
        self.N_exit = self.N_exit0*self.scale_factor
        self.N_halt = self.N_halt0*self.scale_factor
        
        self.E_entrance = self.E_entrance0*self.scale_factor
        self.E_exit = self.E_exit0*self.scale_factor
        self.E_halt = self.E_halt0*self.scale_factor
        
        self.S_entrance = self.S_entrance0*self.scale_factor
        self.S_exit = self.S_exit0*self.scale_factor
        self.S_halt = self.S_halt0*self.scale_factor
        
        self.W_entrance = self.W_entrance0*self.scale_factor
        self.W_exit = self.W_exit0*self.scale_factor
        self.W_halt = self.W_halt0*self.scale_factor
        
        self.center = self.center0*self.scale_factor
        self.radius = self.radius0*self.scale_factor
        
        # We can choose to work with directions (i.e. N) or quarters (i.e. Q1)
        self.Q1_entrance = self.N_entrance
        self.Q1_exit = self.E_exit
        self.Q1_halt = self.N_halt
        
        self.Q4_entrance = self.E_entrance
        self.Q4_exit = self.S_exit
        self.Q4_halt = self.E_halt
        
        self.Q3_entrance = self.S_entrance
        self.Q3_exit = self.W_exit
        self.Q3_halt = self.S_halt
        
        self.Q2_entrance = self.W_entrance
        self.Q2_exit = self.N_exit
        self.Q2_halt = self.W_halt
        
        return None
        
    
    #--------------------------------------------------------------------------
    
    def show(self):
        
        self.axes.imshow(self.image,extent=self.extent)
        self.axes.set_xlim(0,self.xlim)
        self.axes.set_ylim(0,self.ylim)
        try:
            self.figure.show()
        except AttributeError:
            plt.show()

        return None
    
    #--------------------------------------------------------------------------
    
    def build_tracks(self):
        
        # We have +2 as we will remove n = frames_per_move = idx
        # from both the start and end tails of the quarter circle.
        
        # !!!!
        n_pts = (self.size+2)*self.frames_per_move 
        
#        n_pts = int((self.size+3)*self.frames_per_move + self.size)
        self.N = n_pts
#        correction = 1/3 * n_pts
#        n_pts = int(n_pts + correction)
        
        # Setup complete quarter circles with full tails
        
        
        # Q1
        x1,y1 = quarter_circle(self.center,self.radius,Q='Q1',
                               N_pts=n_pts,
                               clockwise=True)
  
        # Q2
        x2,y2 = quarter_circle(self.center,self.radius,Q='Q2',
                               N_pts=n_pts,
                               clockwise=True)
        
        
        # Q3
        x3,y3 = quarter_circle(self.center,self.radius,Q='Q3',
                               N_pts=n_pts,
                               clockwise=True)
        
        
        # Q4
        x4,y4 = quarter_circle(self.center,self.radius,Q='Q4',
                               N_pts=n_pts,
                               clockwise=True)
        
        # Modification: we remove tails of quarter circle.
        
        # This is done such that exits and entrances line-up
        # with the start and end of quarters.
        # To see this, set view_track = True.
        # Note: self.correct_entrances_and_exits() ensures all is lined up.
        
        idx = self.frames_per_move
        
        x1,y1 = x1[idx:-idx],y1[idx:-idx]
        x2,y2 = x2[idx:-idx],y2[idx:-idx]
        x3,y3 = x3[idx:-idx],y3[idx:-idx]
        x4,y4 = x4[idx:-idx],y4[idx:-idx]
        

        # Setup Quarters as 2D coordinates
        n_size = n_pts - 2*idx

        
        self.Q1 = np.zeros((n_size,2))
        self.Q1[:,0] = x1
        self.Q1[:,1] = y1
        self.Q1_start = self.Q1[0]
        self.Q1_start_idx = 0
        self.Q1_end_idx = n_size - 1
        
        self.Q2 = np.zeros((n_size,2))
        self.Q2[:,0] = x2
        self.Q2[:,1] = y2
        self.Q2_start = self.Q2[0]
        self.Q2_start_idx = 3*n_size
        self.Q2_end_idx = 4*n_size - 1
        
        self.Q3 = np.zeros((n_size,2))
        self.Q3[:,0] = x3
        self.Q3[:,1] = y3
        self.Q3_start = self.Q3[0]
        self.Q3_start_idx = 2*n_size
        self.Q3_end_idx = 3*n_size - 1
        
        self.Q4 = np.zeros((n_size,2))
        self.Q4[:,0] = x4
        self.Q4[:,1] = y4
        self.Q4_start = self.Q4[0]
        self.Q4_start_idx = n_size
        self.Q4_end_idx = 2*n_size - 1
        
        # Clockwise
        self.track = np.concatenate((self.Q1,self.Q4,self.Q3,self.Q2))
        
        self.start_idxs = [self.Q1_start_idx,self.Q4_start_idx,
                           self.Q3_start_idx,self.Q2_start_idx]
        
        self.entrances = [self.N_entrance,self.E_entrance,
                          self.S_entrance,self.W_entrance]
        
        self.end_idxs = [self.Q1_end_idx,self.Q4_end_idx,
                         self.Q3_end_idx,self.Q2_end_idx]
        
        self.exits = [self.N_exit,self.E_exit,
                      self.S_exit,self.W_exit]
        
        self.N_bearings = 180
        self.E_bearings = 270
        self.S_bearings = 0
        self.W_bearings = 90
        
        self.bearings = [self.N_bearings,self.E_bearings,
                         self.S_bearings,self.W_bearings]
        
        self.keys = ['N','E','S','W']
        self.Q_keys = ['Q1','Q4','Q3','Q2']
        
        self.N_to_E = self.Q1
        self.E_to_S = self.Q4
        self.S_to_W = self.Q3
        self.W_to_N = self.Q2
        
        self.N_start = self.Q1_start
        self.E_start = self.Q4_start
        self.S_start = self.Q3_start
        self.W_start = self.Q2_start
        
        self.N_start_idx = self.Q1_start_idx
        self.E_start_idx = self.Q4_start_idx
        self.S_start_idx = self.Q3_start_idx
        self.W_start_idx = self.Q2_start_idx
        
        self.N_end = self.Q1[-1]
        self.E_end = self.Q4[-1]
        self.S_end = self.Q3[-1]
        self.W_end = self.Q2[-1]
        
        self.N_end_idx = self.Q1_end_idx
        self.E_end_idx = self.Q4_end_idx
        self.S_end_idx = self.Q3_end_idx
        self.W_end_idx = self.Q2_end_idx
        
        return None
        


    #--------------------------------------------------------------------------
    
    def correct_entrances_and_exits(self):
        
        self.N_entrance[0] = self.N_start[0]
        self.N_exit[0] = self.W_end[0]
        self.N_halt[0] = self.N_start[0]
        
        self.E_entrance[1] = self.E_start[1]
        self.E_exit[1] = self.N_end[1]
        self.E_halt[1] = self.E_start[1]
        
        
        self.S_entrance[0] = self.S_start[0]
        self.S_exit[0] = self.E_end[0]
        self.S_halt[0] = self.S_start[0]
        
        self.W_entrance[1] = self.W_start[1]
        self.W_exit[1] = self.S_end[1]
        self.W_halt[1] = self.W_start[1]
        
        self.halt_zones = [self.N_halt,self.E_halt,
                           self.S_halt,self.W_halt]
        # Halt zones move into start zones.
        # Start zones are the first coordinate of a circle quarter.
        self.start_zones = [self.N_start,self.E_start,
                            self.S_start,self.W_start]
        
        return None

    #--------------------------------------------------------------------------
    
    def view_track(self):
        
        # Plot the trimmed quarters
        self.axes.plot(self.Q2[:,0],self.Q2[:,1],'ro',alpha=0.5)
        self.axes.plot(self.Q3[:,0],self.Q3[:,1],'bo',alpha=0.5)
        self.axes.plot(self.Q4[:,0],self.Q4[:,1],'yo',alpha=0.5)
        self.axes.plot(self.Q1[:,0],self.Q1[:,1],'go',alpha=0.5)
        
        # Plot entrances
        self.axes.plot(*self.Q2_entrance,'ro',alpha=0.5)
        self.axes.plot(*self.Q3_entrance,'bo',alpha=0.5)
        self.axes.plot(*self.Q4_entrance,'yo',alpha=0.5)
        self.axes.plot(*self.Q1_entrance,'go',alpha=0.5)
        
        # Plot exits
        self.axes.plot(*self.Q2_exit,'ro',alpha=0.5)
        self.axes.plot(*self.Q3_exit,'bo',alpha=0.5)
        self.axes.plot(*self.Q4_exit,'yo',alpha=0.5)
        self.axes.plot(*self.Q1_exit,'go',alpha=0.5)
        
        # Plot halting zones
        self.axes.plot(*self.Q2_halt,'ro',alpha=0.5)
        self.axes.plot(*self.Q3_halt,'bo',alpha=0.5)
        self.axes.plot(*self.Q4_halt,'yo',alpha=0.5)
        self.axes.plot(*self.Q1_halt,'go',alpha=0.5)
    
        return None

#------------------------------------------------------------------------------


#if __name__ == '__main__':
#    
#    
#    frames_per_move = 3
#    
#    c = CircleDisplay(size=size.small,frames_per_move=frames_per_move)
#    v = VehicleDisplay(coords=c.W_entrance,bearings=c.W_bearings,axes=c.axes)
#    v.show()
#    # NOTE: appear at entrance and move to halting point.
#    v.move(c.W_halt)
#    v.swivel()  # Swivel and/or shake to show halitng/waiting.
#    v.shake()
#    v.move(c.W_start)
#    v.setup_track(c.track,c.W_start_idx)
#    v.move(c.frames_per_move) # NOTE: we get frames per move from circle object.
#    
#    z = VehicleDisplay(coords=c.W_entrance,bearings=c.W_bearings,axes=c.axes,
#                       color='lightgreen')
#    z.show()
#    z.move(c.W_halt)
#    z.swivel()
#    z.shake()
#    z.move(c.W_start)
#    z.hide()
#    z.reset_bearings(v.bearings)
#    z.show()
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    