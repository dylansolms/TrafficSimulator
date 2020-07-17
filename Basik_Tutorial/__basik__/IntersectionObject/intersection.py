

# !!!!: the shedule_intersection_move() will be similar to that of 
# schedule_on_ramp_move

import numpy as np
from ..utils import dict_to_array,check_tpm



#------------------------------------------------------------------------------

default_probs = {'N':{'N':0,'E':0.1,'S':0.8,'W':0.1},
                 'E':{'N':0.25,'E':0,'S':0.5,'W':0.25},
                 'S':{'N':0.8,'E':0.1,'S':0,'W':0.1},
                 'W':{'N':0.5,'E':0.25,'S':0.25,'W':0}}

#------------------------------------------------------------------------------

default_tpm = dict_to_array(default_probs)

#------------------------------------------------------------------------------


class Intersection(object):
    
    '''A point where multiple vehicle flows meet (maximum of 4) but some vehicles
    have right of way over others (i.e. a higher prioritty). This is in 
    contrast to stop streets where all vehicle flows have the same priortiy
    and hence all vehicles must halt to gain service on a first come first serve
    basis.
    
    In an intersection, main flow vehicles only halt if they want to turn
    right. They halt because a right turn would require them to cross the lane
    of opposite flow which is also a main flow. Henc, main flow vehicles
    only halt for main flow vehicles. In the scenario where a main flow vehicle
    wants to turn right but the opposing main flow vehicle indicates that it 
    will continue ahead or perhaps turns left (such an indicator signal will 
    actually not be visible to the vehicle that wants to turn right so it will
    assume prudently that the vehicle intends to continue forward) then it will
    halt. The other opposing vehicle will not halt. However, in the scenario 
    where two main flow vehicles both want to turn right then both will halt.
    Execution of the turn (service) will then be performed on a first come first
    serve basis determined by which vehicle halted first.
    
    All sub-flow vehicles halt for main flow vehicles until some right of way
    criteria is met. Sub-flow vehicles may be subordinate to main flow vehicles 
    but are of equal priority to eachother. Hence, in the case where two
    sub-flow vehicles assess eachother for right of way (assume no main flow
    vehicles present) then service will be based on first come first serve basis
    determined by which vehicle halted first.
    
    
    Attributes:
    -----------
    entrance_size: int
        This is the equivalent amount of __basik__.node.Nodes objects that must
        be traversed to enter a circle object.
    delay_time: float
        The upper bound of the amount of delay a vehicle incurs after halting
        for another vehicle at the entrance. The actual amount of delay incurred
        is a uniformly distributed variable drawn from numpy.random.uniform(1e-3,delay_time).
    entrances: np.ndarray(dtype=object)
        A numpy array containing all the __basik__.node.Nodes objects that form
        the entrances. Consult keys to see which index corresponds to which 
        entrance. Alternatively, the __basik__.node.Nodes.key will also reveal this.
    exits: np.ndarray(dtype=object)
        A numpy array containing all the __basik__.node.Nodes objects that form
        the exits. Consult keys to see which index corresponds to which exit. 
        Alternatively, the __basik__.node.Nodes.key will also reveal this.
    keys: list
        Allows one to check which index corresonds to which direction.
    main_flow_lookup: list
        A list of booleans two determine which entrance is main flow.
    '''
    
    INTERNAL = True
    
    main_flow_lookup = [True,False,True,False]
    idxs = [0,1,2,3]
    
    size = 1
    delay_time = 0.2
    
    
    #--------------------------------------------------------------------------
    
    
    def __init__(self,N_main_flow_entrance,
                      S_main_flow_entrance,
                      E_sub_flow_entrance,
                      W_sub_flow_entrance,
                      N_exit,
                      S_exit,
                      E_exit,
                      W_exit,
                      tpm=default_tpm,
                      right_of_way_count=2,
                      p_risk=0.3):
        
        '''
        Parameters:
        -----------
        N_main_flow_entrance: __basik__.node.Nodes
            out_node (OUT) of a __basik__.RoadObject.lane.Lane object.
        S_main_flow_entrance: __basik__.node.Nodes
            out_node (OUT) of a __basik__.RoadObject.lane.Lane object.
        E_sub_flow_entrance: __basik__.node.Nodes
            out_node (OUT) of a __basik__.RoadObject.lane.Lane object.
        W_sub_flow_entrance: __basik__.node.Nodes
            out_node (OUT) of a __basik__.RoadObject.lane.Lane object.
        N_exit: __basik__.node.Nodes
            in_node (IN) of a __basik__.RoadObject.lane.Lane object.
        S_exit: __basik__.node.Nodes
            in_node (IN) of a __basik__.RoadObject.lane.Lane object.
        E_exit: __basik__.node.Nodes
            in_node (IN) of a __basik__.RoadObject.lane.Lane object.
        W_exit: __basik__.node.Nodes
            in_node (IN) of a __basik__.RoadObject.lane.Lane object.
        tpm: numpy.ndarray or dict
            A transition probability matrix. It is row stochastic.
            See __basik__.IntersectionObject.intersection.default_probs for an
            example using  a dictionary or
            __basik__.IntersectionObject.intersection.default_tpm for an 
            example using a 2d numpy.ndarray. 
        right_of_way_count: int
            The amount of nodes that must be unoccupied in the direction of flow
            that a vehicle might cross e.g. if a vehicle turns right from South
            to East then it must cross North-to-South flow and will require a
            certain amount of nodes in that flow to be cleared from the point of
            crossing before executing the manuver.
            This must be greater or equal to one.
        p_risk: float
            This probability assigns how readily a vehicle will take a risk
            if it does not strictly have right of way but there is at least one
            node cleared. A high value close to one leads to risky behaviour. 
            Of cource, right_of_way_count plays an integral
            role in risky behaviour as well. right_of_way_count is the perception
            that vehicles vehicles have of what is adequate to give them right
            of way.
        
        '''
        
        self.N_main_flow_entrance = N_main_flow_entrance
        self.S_main_flow_entrance = S_main_flow_entrance
        self.E_sub_flow_entrance = E_sub_flow_entrance
        self.W_sub_flow_entrance = W_sub_flow_entrance
        self.N_exit = N_exit
        self.S_exit = S_exit
        self.E_exit = E_exit
        self.W_exit = W_exit
        
        self.tpm = check_tpm(tpm) # allows for a dictionary, list of lists or 
                                  # numpy array to be given.
                                  
        self.setup_entrances_and_exits()
        
        assert right_of_way_count >= 1
        self.right_of_way_count = right_of_way_count
        assert p_risk >= 0 and p_risk <= 1
        self.p_risk = p_risk
    
    #--------------------------------------------------------------------------
        
    def setup_entrances_and_exits(self):
        
    
        
        self.entrances = np.array([self.N_main_flow_entrance, 
                                   self.E_sub_flow_entrance,
                                   self.S_main_flow_entrance,
                                   self.W_sub_flow_entrance],dtype=object)
    
        self.exits = np.array([self.N_exit,
                               self.E_exit,
                               self.S_exit,
                               self.W_exit],dtype=object)
        
        for idx in range(4):
            
            # Entrances
            self.entrances[idx].service_node = True
            self.entrances[idx].idx = idx
            self.entrances[idx].intersection = self
            self.entrances[idx].intersection_entrance = True
            self.entrances[idx].main_flow = self.main_flow_lookup[idx]
            # Temporary setting below such that front is not None.
            # If front is None then the vehicle becomes disposed.
            self.entrances[idx].front = self.N_exit
            
            # Exits
            self.exits[idx].service_node = True
            self.exits[idx].idx = idx
            self.exits[idx].intersection = self
            self.exits[idx].intersection_exit = True
            self.exits[idx].main_flow = self.main_flow_lookup[idx]
            
    
    
        return None
    
    #--------------------------------------------------------------------------
    
    def choose_exit(self,idx):
        
        self.current_entrance_idx = idx
        self.current_entrance = self.entrances[idx]
        self.current_exit_idx = np.random.choice(a=self.idxs,
                                                 p=self.tpm[idx])
        self.current_exit = self.exits[self.current_exit_idx]
        
        return None
    
    
    #--------------------------------------------------------------------------
            
    def right_of_way(self,entrance_idx,
                          exit_idx,
                          aranged_time):
        
        '''
        A complex function that makes use of helper functions to handle the
        decision making process of vehicle on assessing whether it has a right
        of way based on whether it is part of main or subordinate flow.
        '''
        
        #----------------------------------------------------------------------
        
        if entrance_idx == 0:
            # NORTHERN ENTRANCE (MAIN FLOW)
            
            if exit_idx == 1:
                # Left turn to East: no right of way assessment required.
                return True,aranged_time
            
            elif exit_idx == 2:
                # Proceed forward South: no right of way assessment required.
                return True,aranged_time
            
            elif exit_idx == 3:
                # Cross over the opposing main flow (South to North) 
                # and onto the Western exit.
                
                
#                if (self.S_main_flow_entrance.occupied and
#                    self.S_main_flow_entrance.vehicle.has_waited):
#                    time = self.S_main_flow_entrance.vehicle.time +\
#                           np.random.uniform(1e-3,self.delay_time)
#                    self.S_main_flow_entrance.vehicle.wait = False
#                    self.S_main_flow_entrance.vehicle.move_type = 'partial cross intersection'
#                    return True,time
                
                
                entrances = [self.S_main_flow_entrance] # assess opposing flow.
                proceed,time = self.assess_right_of_way(entrances,
                                                        aranged_time)
                return proceed,time
            
            elif exit_idx == 0:
                raise ValueError('No self transition allowed!')
            else:
                Exception('No cases processed!')
        
        #----------------------------------------------------------------------
        
        elif entrance_idx == 1:
            # EASTERN ENTRANCE (SUB FLOW)
            
            if exit_idx == 0:
                # Cross over both MAIN flows onto Northern exit via a 
                # right turn.
                entrances = [self.N_main_flow_entrance,
                             self.S_main_flow_entrance,
                             self.W_sub_flow_entrance]
#                entrances = [self.N_main_flow_entrance,
#                             self.S_main_flow_entrance]
                proceed,time = self.assess_right_of_way(entrances,
                                                        aranged_time)
                return proceed,time
            
            elif exit_idx == 2:
                # Turn left onto the Southern exit.
                entrances = [self.N_main_flow_entrance]
                proceed,time = self.assess_right_of_way(entrances,
                                                        aranged_time)
                return proceed,time
            
            elif exit_idx == 3:
                # Cross over both the MAIN flows and onto the Western exit.
                entrances = [self.N_main_flow_entrance,
                             self.S_main_flow_entrance]
                proceed,time = self.assess_right_of_way(entrances,
                                                        aranged_time)
                return proceed,time
            
            elif exit_idx == 1:
                raise ValueError('No self transition allowed!')
            else:
                Exception('No cases processed!')
        
        #----------------------------------------------------------------------
            
        elif entrance_idx == 2:
            # SOUTHERN ENTRANCE (MAIN FLOW)
            
            if exit_idx == 0:
                # Proceed forward to North: no right of way assessment required.
                return True,aranged_time
            
            elif exit_idx == 1:
                # Cross over the opposing main flow (North to South) 
                # and onto the Eastern exit.
                
                entrances = [self.N_main_flow_entrance]
                proceed,time = self.assess_right_of_way(entrances,
                                                        aranged_time)
                return proceed,time
            
            elif exit_idx == 3:
                # Turn left onto West: no right of way assessment required.
                return True,aranged_time
            
            elif exit_idx == 2:
                raise ValueError('No self transition allowed!')
            else:
                Exception('No cases processed!')
         
        #----------------------------------------------------------------------
        
        elif entrance_idx == 3:
            # WESTERN ENTRANCE (SUB FLOW)
            if exit_idx == 0:
                # Turn left onto the Northern exit. Joins South-to-North flow.
                entrances = [self.S_main_flow_entrance]
                proceed,time = self.assess_right_of_way(entrances,
                                                        aranged_time)
                return proceed,time
            
            elif exit_idx == 1:
                # Cross over both the MAIN flows and onto the Eastern exit.
                entrances = [self.N_main_flow_entrance,
                             self.S_main_flow_entrance]
                proceed,time = self.assess_right_of_way(entrances,
                                                        aranged_time)
                return proceed,time
            
            elif exit_idx == 2:
                # Cross over both MAIN flows onto Southern exit via a 
                # right turn.
                entrances = [self.N_main_flow_entrance,
                             self.S_main_flow_entrance,
                             self.E_sub_flow_entrance]
#                entrances = [self.N_main_flow_entrance,
#                             self.S_main_flow_entrance]
                proceed,time = self.assess_right_of_way(entrances,
                                                        aranged_time)
                return proceed,time
            
            elif exit_idx == 3:
                raise ValueError('No self transition allowed!')
            else:
                Exception('No cases processed!')
                
        else:
            raise Exception('No cases processed!')
       
    #--------------------------------------------------------------------------

    def assess_right_of_way(self,entrances,
                                 aranged_time):
        '''
        Helper function for right_of_way().
    
        '''

        for entrance in entrances:
            
            
            
            # MAIN FLOW requires several nodes to be assessed.
            if entrance.main_flow:
                
                proceed,time = self.asses_right_of_way_single(entrance,aranged_time)
                if not proceed:
                    return False,time  # a delayed time where rescheduling will take place.
                else:
                    pass
                
            # Assess opposing SUB FLOW entrance.
            else:
                # Right of way is only given if the vehicle's scheduled
                # time is before that of the opposing entrance's vehicle.
                # NOTE: if the other vehicle then tries to move to the same
                # entrance as this vehicle and the entrance is still occupied
                # by this vehicle then Vehicle.move() will handle this by 
                # delaying it and rescheduling an intersection move.
                if entrance.occupied:
                    if aranged_time > entrance.vehicle.time:
                        retry_time = entrance.vehicle.time +\
                                     np.random.uniform(1e-3,self.delay_time)
                        return False,retry_time
                else:
                    pass
        # If all criteria is met then the vehicle is allowed to pass.
        return True,aranged_time
            

    #--------------------------------------------------------------------------


    def asses_right_of_way_single(self,start_node:'entrance node',
                                       aranged_time)->'(boolean,time)':
        
        '''
        Main work-horse function.
        '''
        
        count = 0 # How many node are un-occupied
        
        node = start_node  # should be an exit node
        # Standard while loop
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
                
                
                # CASE 1: Successfully takes a chance at the original aranged time
                # Returns (true,original aranged time)
                if take_chance:
                    has_right_of_way = True
                    return has_right_of_way,aranged_time
                # CASE 2: Right of way is denied. Gives a rescheduled time. 
                # Returns (false,rescheduled time)
                else:
                    retry_time = time +\
                                 np.random.uniform(1e-3,self.delay_time)
                    return has_right_of_way,retry_time
            
            # An additional node has been verified to be un-occupid
            count += 1
            
            # CASE 3: neccessary nodes are cleared and the manuver can be 
            # executed. 
            # Returns (True,original aranged time)
            if count == self.right_of_way_count:
                right_of_way = True
                return right_of_way,aranged_time
            
            # We move to the next node
            node = node.behind 
        
        raise Exception('No cases were processed.')
            
            
    #--------------------------------------------------------------------------
            
    def __repr__(self):
        return 'Intersection ({0})'.format(hex(id(self)))
            
    #--------------------------------------------------------------------------
            
            
            
            
            
            
            
        
        
        