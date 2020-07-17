

import numpy as np



class OffRamp(object):
    
    '''
    A vehicle either continues forward or transitions smoothly off of the 
    main flow. No halting occurs, however, a vehicle may correct its speed
    if it finds vehicles ahead at the off ramp.
    '''
    
    size = 2 # The equivalent amount of nodes traversed
    
    INTERNAL = True
    
    #--------------------------------------------------------------------------
    
    def __init__(self,offramp_lane_entrance,
                      offramp_lane_on_exit,
                      offramp_lane_off_exit,
                      standard_lane_entrance,
                      standard_lane_exit,
                      off_prob=0.2):
        
        '''
        Parameters:
        ------------
        offramp_lane_entrance: __basik__.node.Node
            The off-ramp starts here.
            out_node (OUT) of __basik__.RoadObject.lane.Lane
        offramp_lane_on_exit: __basik__.node.Node
            The vehicle remains on the current flow.
            in_node (IN) of __basik__.RoadObject.lane.Lane
        offramp_lane_off_exit: __basik__.node.Node
            The vehicle moves off of the the current flow and exits here.
            in_node (IN) of __basik__.RoadObject.lane.Lane
        standard_lane_entrance: __basik__.node.Node or None
            The lane of opposing flow is just a standard lane that permits flow
            forward. An opposing lane does not need to exist. This is done
            by setting the standard_lane_entrance and standard_lane_exit both
            to None.
            out_node (OUT) of __basik__.RoadObject.lane.Lane
        standard_lane_exit: __basik__.node.Node
            The lane of opposing flow is just a standard lane that permits flow
            forward. An opposing lane does not need to exist. This is done
            by setting the standard_lane_entrance and standard_lane_exit both
            to None.
            in_node (IN) of __basik__.RoadObject.lane.Lane
        off_prob: float
            The probability that a vehicle at offramp_lane_entrance transitions
            to offramp_lane_off_exit. It is natural to assume that this might
            be less than 0.5, however, any values between zero and one is
            permitted.
        '''
        
        self._create_tpm(off_prob)
        self._setup_entrance_and_exits(offramp_lane_entrance,
                                       offramp_lane_on_exit,
                                       offramp_lane_off_exit,
                                       standard_lane_entrance,
                                       standard_lane_exit)
        
    
    #--------------------------------------------------------------------------
    
    def _create_tpm(self,off_prob):
        self.off_prob = off_prob  # prob of turining off
        self.on_prob = 1 - off_prob   # prob of continuing on
        self.tpm = np.array([self.off_prob,self.on_prob])
        self.keys = ['OFF','ON']
        self.idxs = [0,1]
        return None
    
    #--------------------------------------------------------------------------
    
    def _setup_entrance_and_exits(self,offramp_lane_entrance,
                                       offramp_lane_on_exit,
                                       offramp_lane_off_exit,
                                       standard_lane_entrance,
                                       standard_lane_exit):
        

        
        ### Entrance  ###
        
        # Off-ramp entrance first
        offramp_lane_entrance.service_node = True
        offramp_lane_entrance.off_ramp_entrance = True
        offramp_lane_entrance.off_ramp = self
        offramp_lane_entrance.front = offramp_lane_on_exit  # temporary default setting
        self.entrance = offramp_lane_entrance
        # Deal with the standard lane
        standard_lane_entrance.service_node = True
        standard_lane_entrance.off_ramp_standard_entrance = True
        standard_lane_entrance.off_ramp = self
        standard_lane_entrance.front = standard_lane_exit  # permanent
        self.other_entrance = standard_lane_entrance
        
        ### Exits  ###
        
        self.exits = np.zeros(2,dtype=object)
        
        # Off ramp exit node
        offramp_lane_off_exit.behind = offramp_lane_entrance  # permanent
        offramp_lane_off_exit.service_node = True
        offramp_lane_off_exit.off_ramp_exit = True
        offramp_lane_off_exit.off_ramp = self
        self.exits[0] = offramp_lane_off_exit
        
        # Off ramp remain on road
        offramp_lane_on_exit.behind = offramp_lane_entrance  # permanent
        offramp_lane_on_exit.service_node = True
        offramp_lane_on_exit.off_ramp_exit = True
        offramp_lane_on_exit.off_ramp = self
        self.exits[1] = offramp_lane_on_exit
        
        # Deal with standard lane
        standard_lane_exit.service_node = True
        standard_lane_exit.behind = standard_lane_entrance
        standard_lane_exit.off_ramp_standard_exit = True
        standard_lane_exit.off_ramp = self
        self.other_exit = standard_lane_exit
        
            
        return None
    
    #--------------------------------------------------------------------------
    
    def choose_exit(self):
        self.chosen_exit_idx =  int(np.random.choice(a=self.idxs,p=self.tpm))
        self.chosen_exit_key = self.keys[self.chosen_exit_idx]
        self.chosen_exit = self.exits[self.chosen_exit_idx]
        
        return self.chosen_exit
    
    #--------------------------------------------------------------------------
        
    def entrance_locked(self):
        return self.entrance.occupied
    
    #--------------------------------------------------------------------------


#------------------------------------------------------------------------------










