
import numpy as np




#------------------------------------------------------------------------------
    
class OnRamp(object):
    
    '''A subordinate flow is allowed to join some main flow at this point.
    The subordinate flow will halt at the on-ramp. Main flow vehicles will 
    not halt for subordinate flow vehicles. They might, however, correct their
    velocity if a subordinate flow has passed onto the main flow and is 
    travelling at a lower velocity.
    
    Attributes:
    -----------
    size: int
        The equivalent amount of nodes to be traversed in order for a subordinate
        vehicle to enter the main flow
    delay_time: float
        If a sub-flow vehicle halts and moves again then a delay is produced
        by the vehicles lack in ability to respond immediately. This additional
        delay incurred is normally distributed as
        delay = np.random.uniform(1e-3,delay_time)
    '''
    
    INTERNAL = True
    
    size = 2  # The equivalent amount of nodes traversed
    delay_time = 0.2
    #--------------------------------------------------------------------------

    def __init__(self,main_flow_entrance,
                      sub_flow_entrance,
                      on_ramp_exit,
                      standard_lane_entrance,
                      standard_lane_exit,
                      right_of_way_count=2,
                      p_risk=0.3):
        
        '''
        Parameters:
        -----------
        main_flow_entrance: __basik__.node.Node
            Main flow starts here.
            out_node (OUT) of __basik__.RoadObject.lane.Lane
        sub_flow_entrance: __basik__.node.Node
            Subordinate flow that intends to join the main flow.
            out_node (OUT) of __basik__.RoadObject.lane.Lane
        on_ramp_exit: __basik__.node.Node
            The exit of main flow. Vehicles from both main_flow_entrance and
            sub_flow_entrance will be found crossing here.
            in_node (IN) of __basik__.RoadObject.lane.Lane
        standard_lane_entrance: __basik__.node.Node
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
        right_of_way_count: int
            The amount of cleared nodes required to the right of a subordinate
            flow vehicle if it wishes to join the main flow at the on-ramp.
        p_risk: float
            This probability assigns how readily a vehicle will take a risk
            if it does not strictly have right of way but there is at least one
            node cleared. A high value close to one leads to risky behaviour. 
            Of cource, right_of_way_count plays an integral
            role in risky behaviour as well. right_of_way_count is the perception
            that vehicles vehicles have of what is adequate to give them right
            of way.
        '''
        
        self._setup_entrance_and_exits(main_flow_entrance,
                                       sub_flow_entrance,
                                       on_ramp_exit,
                                       standard_lane_entrance,
                                       standard_lane_exit)
        
        assert right_of_way_count >= 1
        self.right_of_way_count = right_of_way_count
        assert p_risk >= 0 or p_risk <= 1
        self.p_risk = p_risk
        
    #--------------------------------------------------------------------------
        
        
    def _setup_entrance_and_exits(self,main_flow_entrance,
                                       sub_flow_entrance,
                                       on_ramp_exit,
                                       standard_lane_entrance,
                                       standard_lane_exit):
        
        ### ENTRANCES  ###
        
        # MAIN FLOW
        main_flow_entrance.service_node = True
        main_flow_entrance.on_ramp = self
        main_flow_entrance.on_ramp_node = True
        main_flow_entrance.sub_flow = False
        main_flow_entrance.front = on_ramp_exit
        
        # SUB FLOW
        sub_flow_entrance.service_node = True
        sub_flow_entrance.on_ramp = self
        sub_flow_entrance.on_ramp_node = True
        sub_flow_entrance.sub_flow = True    # Only difference to main flow
        sub_flow_entrance.front = on_ramp_exit
        
        self.main_flow_entrance = main_flow_entrance
        self.sub_flow_entrance = sub_flow_entrance
        
        self.entrances = np.array([main_flow_entrance,
                                   sub_flow_entrance],dtype=object)
    
        # Deal with standard lane
        standard_lane_entrance.service_node = True
        standard_lane_entrance.on_ramp_standard_node = True
        standard_lane_entrance.on_ramp_node = False # unncecessary but for emphasis
        standard_lane_entrance.front = standard_lane_exit
        standard_lane_entrance.on_ramp = self
        self.other_entrance = standard_lane_entrance
        
        ### EXITS  ###
        
        # Exit where the two flows meet
        on_ramp_exit.service_node = True
        on_ramp_exit.on_ramp = self
        on_ramp_exit.on_ramp_exit = True
        on_ramp_exit.behind = main_flow_entrance  # does change (temp default)
        
        self.exit = on_ramp_exit
        
        # Deal with standard lane
        standard_lane_exit.service_node = True
        standard_lane_exit.on_ramp = self
        standard_lane_exit.on_ramp_exit = True
        standard_lane_exit.behind = standard_lane_entrance  # permanent
        self.other_exit = standard_lane_exit
    
        return None

    
    #--------------------------------------------------------------------------
    
    
    def right_of_way(self,aranged_time):
        
        count = 0 # How many nodes are un-occupied to the right of the
        # vehicle that wants to enter the main flow
        
        node = self.main_flow_entrance
        
        while True:
            
            if node.occupied:
                
                has_right_of_way = False
                time = node.vehicle.time
                take_chance = False
                
                if aranged_time < time and count >= 1:
                    # To take a chance at least one node must be cleared.
                    # The chance-taker should also have the knowledge that 
                    # it will move before the vehicle occupying the node
                    # in question
                    take_chance = np.random.uniform(0,1) <= self.p_risk
                    
                if take_chance:
                    has_right_of_way = True
                    return has_right_of_way,aranged_time
                else:
                    retry_time = time +\
                                 np.random.uniform(1e-3,self.delay_time)
                    return has_right_of_way,retry_time
            
            # An additional node has been verified to be un-occupid
            count += 1
            
            
            if count == self.right_of_way_count:
                right_of_way = True
                return right_of_way,aranged_time
            
            # We move to the next node
            node = node.behind 
        
        raise Exception('No cases were processed.')
            
            
    #--------------------------------------------------------------------------
                
                
    
#------------------------------------------------------------------------------
        
        
        
        
        
        
        
        
        
        
        
        
        
        