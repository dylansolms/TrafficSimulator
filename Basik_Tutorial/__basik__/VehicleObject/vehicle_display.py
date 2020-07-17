
import matplotlib.pyplot as plt
import numpy as np
#import math as m
from scipy.ndimage import rotate

from ..utils import rotate_coord,get_bearings,orthogonal,bearings_to_vector

from .vehicle_colors import color_list

from .preloaded_vehicle_images import vehicle_image_arrays

#------------------------------------------------------------------------------

class VehicleDisplay(object):
    
    DISPLAY = True
    
    speed_up_factor = 1
    SHOW = True
    # Setting SHOW to False will allow the vehicle to move within the 
    # various display components to acquire the coordinates and tracks that
    # are required such that the simulation's internal mechanism may agree
    # with the display. All this is done without the vehicle's image being 
    # displayed. This allows the simulation to to run much faster as it 
    # bypasses the time-costly rotate function from scipy.ndimage as well as
    # skipping matplotlib.pyplots.pause().

    #--------------------------------------------------------------------------
    
    def __init__(self,coords=[0,0],color='random',bearings=90,
                      axes=None,track=None,current_track_idx=0,
                      length=10,width=5):
        
        
        self.length = length
        self.width = width
        assert len(coords) == 2
        self.coords = np.array(coords,dtype=np.float64)  # center of the object
        self.bearings = bearings
        
        assert isinstance(color,str)
        if color not in color_list:
            string = 'Please chose one of the colors:'+\
            '\n{0}'.format(color_list)
            raise Exception(string)
        if color == 'random':
            self.color = np.random.choice(a=color_list)
            while self.color == 'random':
                # Pick until we do not choose random
                self.color = np.random.choice(a=color_list)
        else:
            self.color = color
            
        
#        self.path = './Images/cars/{0}.png'.format(self.color)
        # Put the image in its standard position (0 degrees bearings)
        # Rotate 90 anti-clockwise
#        self.image = rotate(plt.imread(self.path),90,reshape=True)
#        self.image = scale255(self.image)
        self.image = rotate(vehicle_image_arrays[self.color],
                            90,reshape=True)
        
        self.axes = axes
 
        self.top_right = self.coords + 0.5*np.array([self.width,self.length])
        self.top_left = self.coords + 0.5*np.array([-self.width,self.length])
        self.bottom_right = self.coords + 0.5*np.array([self.width,-self.length])
        self.bottom_left = self.coords + 0.5*np.array([-self.width,-self.length])
        
        self.corners = [self.top_right,self.top_left,
                        self.bottom_right,self.bottom_left]
        
        self.track = None
        self.setup_track(track,current_track_idx)
        
        assert self.speed_up_factor > 0
        
        
        
    #--------------------------------------------------------------------------
    
    @property
    def extent(self):
        
        '''
        Extent is used by Matplotlibs imshow function. It is the minimal set
        of coordinates used to describe the rectangle that completely contains
        the image. This is important for when the image is rotated such that
        no distortions ocurr.
        '''
        
        new_corners = np.zeros((4,2))
        
        for idx,corner in enumerate(self.corners):
            
            new_corner = rotate_coord(origin=self.coords,
                                      coord=corner,
                                      angle=self.bearings)
            new_corners[idx] = new_corner
        
        min_x = new_corners[:,0].min()
        max_x = new_corners[:,0].max()
        min_y = new_corners[:,1].min()
        max_y = new_corners[:,1].max()
        
        return [min_x,max_x,min_y,max_y]
            
    #--------------------------------------------------------------------------
    
    def show(self):
        
        if not self.SHOW:
            return None
        
        if self.axes is None:
#            raise ValueError('An axes has to plot on has not yet been provided.')
            return None
        
        # For rotation we use - as to allow for bearings to adhere to the
        # convention of clock-wise direction starting from North.
        rotated_image = rotate(self.image,-self.bearings,reshape=True)
        # Note: it was important to put it into an array form such that
        # Matplotlib can resize it using extent.
        
        
        
        
        self.image_plot = self.axes.imshow(rotated_image,
                                           extent=self.extent)
        
        plt.show()
        
        return None
    
    #--------------------------------------------------------------------------
    
    def hide(self):
        
        if not self.SHOW:
            return None
        
        if hasattr(self,'image_plot'):
            try:
                self.image_plot.remove()
            except ValueError:
                # ValueError: list.remove(x): x not in list
                pass
    
            
        return None
        
    
    #--------------------------------------------------------------------------

    def reset_bearings(self,new_bearings):
        self.bearings = new_bearings
        return None
    
    #--------------------------------------------------------------------------
    
    def adjust_bearings(self,adjustment):
        self.bearings += adjustment
        return None
    
    #--------------------------------------------------------------------------
    
    def reset_axes(self,new_axes,hide=False):
        if hide:
            self.hide()
        self.axes = new_axes
        return None
    
    #--------------------------------------------------------------------------
    
    def reset_coords(self,new_coords):
        self.coords = np.array(new_coords)
        self.top_right = self.coords + 0.5*np.array([self.width,self.length])
        self.top_left = self.coords + 0.5*np.array([-self.width,self.length])
        self.bottom_right = self.coords + 0.5*np.array([self.width,-self.length])
        self.bottom_left = self.coords + 0.5*np.array([-self.width,-self.length])
        
        self.corners = [self.top_right,self.top_left,
                        self.bottom_right,self.bottom_left]
        return None
    
    #--------------------------------------------------------------------------
    
    def adjust_coords(self,delta:'[x,y]'):
        self.coords += delta
        self.top_right += delta
        self.top_left += delta
        self.bottom_right += delta
        self.bottom_left += delta
        return None
    
    #--------------------------------------------------------------------------
    
    def get_bearings(self,start_pt,end_pt):
        return get_bearings(start_pt,end_pt)
    
    #--------------------------------------------------------------------------
    
    def setup_track(self,track,current_track_idx):

        # TODO: deal with list dilemma
        if track is not None:
#            assert isinstance(track,list)
#            # Note we raise assertion error and do not convert the track object
#            # to a list. If we had done this, we would create a new object in
#            # memory which would lead to big chunks of memory being used in a
#            # redundant manner. We want to maintain the fact that self.track
#            # is simply a pointer to some stored track object. This holds for
#            # all the vehicles using this track.
#            if list(self.coords) not in track:
#                raise ValueError('coords not in given track.')
            self.track = None
            pass
        else:
            return None
                
        self.track = track  # list of 2D coordinates
        assert isinstance(current_track_idx,int)
        
        self.current_track_idx = current_track_idx
        self.track_start_idx = 0
        self.track_end_idx = len(track) - 1
        
        # Below is done for cyclic behaviour. Placing a None in the track
        # serves as a break-point in the cyclic behaviour.
        if self.current_track_idx == self.track_end_idx:
            self.next_track_idx = self.start_idx
        else:
            self.next_track_idx = self.current_track_idx + 1
    
        return None
    
    #--------------------------------------------------------------------------
        
    def cycle_track(self):
        # Note we do not use cycle_list from utils to cycle through the
        # track. This would require us to make self.track a new copy 
        # of the original track and not a pointer to it. This would use a lot
        # of redundant memory. It would need to be a new copy with a unique
        # memory id() because cycle_list permanently changes the list fed
        # into it as an argument.
        if self.track is None:
            return None
        
        if len(self.track[0]) != 2: 
            raise ValueError('')
            
        if self.current_track_idx == self.track_end_idx:
            self.current_track_idx = self.track_start_idx
            self.next_track_idx = self.current_track_idx + 1
        elif self.current_track_idx == self.track_end_idx - 1:
            self.current_track_idx = self.track_end_idx
            self.next_track_idx = self.track_start_idx
        else:
            self.current_track_idx += 1
            self.next_track_idx = self.current_track_idx + 1
            
        return self.track[self.current_track_idx]
    
    #--------------------------------------------------------------------------
    
    @property
    def next_track_coord(self):
        '''
        Use this to look ahead to see if the next entry is a None.
        A None implies we must changes axes for plotting.
        '''
        return self.track[self.next_track_idx]

    #--------------------------------------------------------------------------
    
    def single_move(self,destination,
                         time=1,frames=10,hide=False):
        
        # Note that multiple frames produce movement. The movement all takes
        # place in one direction.
        
        destination = np.array(destination)
        assert isinstance(frames,int) and frames > 0
        
        # single_move() is the workhorse function used by all the other
        # move related functions. Hence, we can handle the speed-up
        # factor here only. 
        time_per_frame = abs(time/frames)/self.speed_up_factor  # !!!! PATCH
        adjuistment_per_frame = (destination - self.coords)/frames
        
        frame_count = 0
        
        # Reset the bearings
        new_bearings = self.get_bearings(start_pt=self.coords,
                                         end_pt=destination)
        self.reset_bearings(new_bearings)
        
        # Now peform the linear move
        

        
        while True:

            self.hide()
            self.adjust_coords(adjuistment_per_frame)
            if hide:
                pass
            else:
                self.show()
            plt.pause(time_per_frame)
            frame_count += 1
            if frame_count == frames:
                break
        # By the end of the loop we should be at destination
        
        return None
    
    #--------------------------------------------------------------------------
    
    def multi_move(self,destinations,
                        time_per_move=1,frames_per_move=10,hide=False):
        
        for destination in destinations:
            self.single_move(destination,time_per_move,frames_per_move,hide)
        
        return None
    
    #--------------------------------------------------------------------------
    
    def move_along_track(self,moves=1,
                              time_per_move=1,frames_per_move=10,hide=False):
        assert isinstance(moves,int)
        for move in range(moves):
            destination = self.cycle_track()  # get the next coordinate on the track
            if destination is None:
                # TODO: change to the next component
                pass
            self.single_move(destination,time_per_move,frames_per_move,hide)
            
            
        return None
            
    #--------------------------------------------------------------------------
        
    def move(self,destination,
                  time_per_move=1,frames_per_move=10,hide=False):
        
        if isinstance(destination,int):
            self.move_along_track(destination,
                                  time_per_move,frames_per_move,hide)
        elif np.ndim(destination) == 1:
            self.single_move(destination,time_per_move,frames_per_move,hide)
        else:
            self.multi_move(destination,time_per_move,frames_per_move,hide)
            
        return None
        
    #--------------------------------------------------------------------------
    
    # NOTE: shake, swivel and flicker are animations that consist of two
    # parts. Hence, the use time_per_half.
    
    
    def shake(self,n_shakes=3,shift_percentage=2,time_per_shake=0.1):
        
        u = bearings_to_vector(self.bearings)
        # convert bearings into a direcion vector
        v = orthogonal(u)  # orthogonal unit vector
        perturb = shift_percentage/100*self.width
        coord1 = self.coords + perturb*v
        coord2 = self.coords - perturb*v
        
        original_coords = self.coords # reset_coords overwrites the original
        
        time_per_half_shake = time_per_shake/2
        time_per_half_shake /= self.speed_up_factor
        
        for nth_shake in range(n_shakes):
            self.reset_coords(coord1)
            self.hide()
            self.show()
            plt.pause(time_per_half_shake)
            self.reset_coords(coord2)
            self.hide()
            self.show()
            plt.pause(time_per_half_shake)
        
        self.u = u
        self.v = v
        self.reset_coords(original_coords)
        self.hide()
        self.show()
        
        return None
    
    #--------------------------------------------------------------------------

        
    def swivel(self,n_swivels=3,degrees=3,time_per_swivel=0.1):
        
        original_bearings = self.bearings
        
        bearings1 = self.bearings + degrees
        bearings2 = self.bearings - degrees
        
        time_per_half_swivel = time_per_swivel/2
        time_per_half_swivel /= self.speed_up_factor
        
        for nth_swivel in range(n_swivels):
            self.reset_bearings(bearings1)
            self.hide()
            self.show()
            plt.pause(time_per_half_swivel)
            self.reset_bearings(bearings2)
            self.hide()
            self.show()
            plt.pause(time_per_half_swivel)
            
        self.reset_bearings(original_bearings)
        self.hide()
        self.show()
        
        return None
    
    #--------------------------------------------------------------------------
    
    def flicker(self,n_flickers=3,time_per_flicker=0.1):
        
        time_per_half_flicker = time_per_flicker/2
        time_per_half_flicker /= self.speed_up_factor
        
        for nth_flicker in range(n_flickers):
            
            self.hide()
            plt.pause(time_per_half_flicker)
            self.show()
            plt.pause(time_per_half_flicker)
            
        self.hide()
        
        return None
        
    
    #--------------------------------------------------------------------------
    
        
    def __repr__(self):
        return 'Car ({0})'.format(hex(id(self)))
    
    #--------------------------------------------------------------------------
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

