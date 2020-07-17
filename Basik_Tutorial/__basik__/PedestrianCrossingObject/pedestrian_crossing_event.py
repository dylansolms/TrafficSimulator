
import numpy as np
from ..global_queue import Queue

#from traffic_light_display import TrafficLightDisplay

#------------------------------------------------------------------------------



class PedestrianCrossingEvent(object):
    
    '''
    Put this in the heap along with vehicles.
    Extract it from the heap at its start time to change the current cycle.
    '''
    
    def __init__(self,start_time,end_time,pedestrian_crossing=None):
        self.time = start_time
        self.start_time = start_time
        self.end_time = end_time
        self.pedestrian_crossing = pedestrian_crossing
        self.is_obstruction = True
        self.do_activate = True


    #--------------------------------------------------------------------------
    
    def activate(self):
        
        # Lock the the node after the crosswalk such that it cannot be
        # transitioned to from the node before the crosswalk.
        self.pedestrian_crossing.lock()
        self.pedestrian_crossing.update_unlock_time(self.end_time)
    
        # Show pedestrians.
        if self.pedestrian_crossing.display is not None :
            pedestrian_crossing_display = self.pedestrian_crossing.display
            pedestrian_crossing_display.show_pedestrians()
            
        # Update the time such that the event can be placed back into the
        # heap in order to de-activate the crossing
        self.time = self.end_time 
        self.do_activate = False
        Queue.push(self)  # awaiting extraction for de-activation.

        return None       
    
    #--------------------------------------------------------------------------
    
    def deactivate(self):
        
        
        self.pedestrian_crossing.unlock()
        
        # Hide pedestrians if there is some display component.
        if self.pedestrian_crossing.display is not None :
            pedestrian_crossing_display = self.pedestrian_crossing.display
            pedestrian_crossing_display.hide_pedestrians()
        
        return None

    
    #--------------------------------------------------------------------------
    
    def __eq__(self,other):
        return self.time == other.time
    
    #--------------------------------------------------------------------------
    
    def __lt__(self,other):
        return self.time < other.time
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Pedestrian Crossing Event ({0})'.format(self.time)



#------------------------------------------------------------------------------


