
import numpy as np
#from Types import Lane,Node,Vehicle
from ..RoadObject import Lane
from ..node import Node
from collections import namedtuple

#-------------------------------------------------------------------------------       

#default_transitions = {'N':{'E':0.2,'S':0.6,'W':0.2},
#                       'E':{'S':0.2,'W':0.6,'N':0.2},
#                       'S':{'W':0.3,'N':0.4,'E':0.3},
#                       'W':{'N':0.3,'E':0.4,'S':0.3}}

default_transitions = {'N':{'N':0.25,'E':0.25,'S':0.25,'W':0.25},
                       'E':{'N':0.25,'E':0.25,'S':0.25,'W':0.25},
                       'S':{'N':0.25,'E':0.25,'S':0.25,'W':0.25},
                       'W':{'N':0.25,'E':0.25,'S':0.25,'W':0.25}}
           
#-------------------------------------------------------------------------------

_Size = namedtuple('sizes','small medium large')
size = _Size(small=3,medium=5,large=7)       

#-------------------------------------------------------------------------------


default_in = {'N':Node(),'E':Node(),'S':Node(),'W':Node()}

#-------------------------------------------------------------------------------       
 
default_out = {'N':Node(),'E':Node(),'S':Node(),'W':Node()} 

#-------------------------------------------------------------------------------  


class Circle(object):
    
    '''Traffic Circle with four entrances and exits that permits clock-wise
    flow.
    
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
    tpm: numpy.ndarray
        A transition probability matrix. It is row stochastic.
    '''
    
    INTERNAL = True
    
    entrance_size = 2
    delay_time = 0.1
    
    
    def __init__(self,in_nodes=default_in,
                      out_nodes=default_out,
                      transitions=default_transitions,
                      size=size.medium,
                      right_of_way_count:int=2,
                      p_risk:float=0.3,
                      within_velocity:'m/s'=8.3):  # 8.3 m/s is about 30 km/h
        
        '''
        Parameters:
        -----------
        in_nodes: dict()
            A dictionary of nodes that serve as entrances.
            e.g. {'N':Node(),'E':Node(),'S':Node(),'W':Node()}
        out_nodes: dict()
            A dictionary of nodes that serve as exits.
            e.g. {'N':Node(),'E':Node(),'S':Node(),'W':Node()}
        transitions: dict()
            A dictionary that will be converted to a 2d numpy.ndarray.
            It must be row stochastic. It determines which exit will be selected
            by a vehicle from a given entrance. Note that we do allow a vehicle
            to go once around a circle entirely to exit at the where it entered.
        size: __basik__.CircleObject.circle.size or 3,5, or 7
            The amount of nodes used to build a quarter of the circle.
        right_of_way_count: int
            The amount of circle nodes that must be unoccupied to the right
            of a vehicle for it to have the right of way to enter the circle.
            This must be greater or equal to one.
        p_risk: float
            This probability assigns how readily a vehicle will take a risk
            if it does not strictly have right of way but there is at least one
            node cleared. A high value close to one leads to risky behaviour
            at a traffic circle. Of cource, right_of_way_count plays an integral
            role in risky behaviour as well. right_of_way_count is the perception
            that vehicles vehicles have of what is adequate to give them right
            of way.
        within_velocity: float
            This is the velocity in meters per second that a vehicle will travel
            withing the circle. 
        '''
        
        
        
        # Asses that all transition probabilties sum up to one
        self._check_transitions(transitions)
        # Convert the use-friendly dictionary into a transition probability matrix
        self._create_tpm()
        # Connect in nodes to decision nodes which connect to choice nodes
        # which can be chosen. These are conncected to out nodes.
        self._create_quarters(size)
        self._setup_entrances_and_exits(in_nodes,out_nodes)
        assert self.entrances[0].front is not None
        
        
        self.unlock_time = None
        self.n_requests = 0
        self.keys = ['N','E','S','W']
        assert isinstance(right_of_way_count,int)
        assert right_of_way_count < size
        # right_of_way_count is the amount of nodes required to be left open
        # from the right of the entrance for it to be allowed to be used
        assert size == 3 or size == 5 or size == 7
        self.size = size
        assert right_of_way_count >= 1
        self.right_of_way_count = right_of_way_count
        # e.g. if set to 2 --> 2 nodes to the left must not be occupied
        assert p_risk >= 0 or p_risk <= 1
        self.p_risk = p_risk
        # Probability of risk assigns how readily a vehicle may take a chance
        # when it does not strictly have right of way i.e. its count of cleared
        # nodes does not satisfy that of right_of_way_count
#        assert p_prudent >= 0 or p_prudent <= 1
#        self.p_prudent = p_prudent
        
        assert within_velocity >= 0
        self.within_velocity = within_velocity
        
    #--------------------------------------------------------------------------
                
    def _check_transitions(self,transitions):
        '''
        Checks that all transition probabilties sum up to one.
        Also creates self.transitions
        '''
        self.keys = ['N','E','S','W']
        self.idxs = [0,1,2,3]
        for key in self.keys:
            sum_ = sum(list(transitions[key].values()))
            if sum_ != 1:
                raise ValueError('transitions at {0} does not sum up to one.'
                                                                   .format(key))
        self.transitions = transitions
        return None
        
    #--------------------------------------------------------------------------
        
    def _create_tpm(self):
        '''
        Converts the dictionary into a numoy array.
        Creates self.tpm
        '''
        self.tpm = np.zeros((4,4))
        self.idx = {'N':0,'E':1,'S':2,'W':3}
        self.exit_idx = {'N':3,'E':0,'S':2,'W':2}
        for key1 in self.keys:
            idx1 = self.idx[key1]
            for key2 in self.transitions[key1].keys():
                try:
                    idx2 = self.idx[key2]
                    self.tpm[idx1,idx2] = self.transitions[key1][key2]
                except KeyError:
                    pass
        return None
    
    #--------------------------------------------------------------------------
    
    def _create_quarters(self,size):
        self.Q_NE = Lane(size,circle_node=True)
        self.Q_ES = Lane(size,circle_node=True)
        self.Q_SW = Lane(size,circle_node=True)
        self.Q_WN = Lane(size,circle_node=True)
        # N to E  (idx:0)
        self.Q_NE.in_node.behind = self.Q_WN.out_node
        self.Q_NE.out_node.front = self.Q_ES.in_node
        # E to S  (idx:1)
        self.Q_ES.in_node.behind = self.Q_NE.out_node
        self.Q_ES.out_node.front = self.Q_SW.in_node
        # S to W  (idx:2)
        self.Q_SW.in_node.behind = self.Q_ES.out_node
        self.Q_SW.out_node.front = self.Q_WN.in_node
        # W to N  (idx:3)
        self.Q_WN.in_node.behind = self.Q_SW.out_node
        self.Q_WN.out_node.front = self.Q_NE.in_node
        # Create quarters array
        self.quarters = [self.Q_NE,self.Q_ES,self.Q_SW,self.Q_WN]
        return None
        
    #--------------------------------------------------------------------------
    
    def _setup_entrances_and_exits(self,in_nodes,out_nodes):
        
        self.entrances = np.zeros(4,dtype=object)
        self.exits = np.zeros(4,dtype=object)
        
#        exit_idxs = [3,0,1,2]
#        exit_idxs = [0,1,2,3]
        self.exit_idxs = [3,0,1,2]
#        for idx,key in enumerate(self.keys):
        for idx in range(4):
            
            key = self.keys[idx]
            entrance_node = in_nodes[key]
            
            if entrance_node is not None:
                entrance_node.service_node = True
                entrance_node.circle_entrance = True
                entrance_node.circle = self
                entrance_node.idx = idx
                entrance_node.key = key
                entrance_node.front = self.quarters[idx].in_node
                if entrance_node.front is None:
                    raise Exception('front is None')
                else:
                    print(entrance_node.front)
                self.entrances[idx] = entrance_node
            else:
                self.entrances[idx] = None
                
            if self.entrances[idx].front is None:
                raise Exception('front is None')
            
            exit_node = out_nodes[key]
            
            exit_idx = self.exit_idxs[idx]
            
            if exit_node is None:
                exit_node = Node()
            
            exit_node.service_node = True
            exit_node.circle_exit = True
            exit_node.circle = self
            exit_node.idx = exit_idx
            exit_node.key = key
            
            exit_node.behind = self.quarters[exit_idx].out_node
            self.quarters[exit_idx].out_node.left = exit_node
            self.exits[idx] = exit_node
            
        return None
    
    #--------------------------------------------------------------------------
    
    
    def entrance_locked(self,entrance):
        locked = entrance.front.occupied
        return locked
    
    #--------------------------------------------------------------------------
    
    def request_unlock_time(self,entrance):
        time = entrance.front.vehicle.time # When the vehicle infront of
        # the entrance is scheduled to move
        return time + 1e-3
    
    #--------------------------------------------------------------------------
    
    def right_of_way(self,entrance,aranged_time):
        
        # Vehicle is at the entrance and wants to enter circular flow
        # It would like to enter one of the quarters.
        
        count = 0  
        node = entrance.front  # first node in the circle
        # This node is a node in one of the quarters.
        
        # We know entrance.front to be free as we have already checked it
        # via entrance_locked
        
        # !!!!
#        node = node.behind     # first node to the left of it. Is it cleared ???
        
        while True:
            
            if node.occupied:
                has_right_of_way = False
                time = node.vehicle.time
                take_chance = False
                if aranged_time < time and count >= 1: 
                    # The two above criteria allow for a risk to be taken
                    # without a crash.
                    take_chance = np.random.uniform(0,1) <= self.p_risk
                if take_chance:
                    has_right_of_way = True
                    return has_right_of_way,aranged_time
                else:
#                    retry_time = time + 1e-6
                    retry_time = time +\
                                 np.random.uniform(1e-3,self.delay_time)
                    return has_right_of_way,retry_time

                
            count += 1  # an additional node to the left is known to be clear
            if count == self.right_of_way_count:
                right_of_way = True
                return right_of_way,aranged_time
            
    #--------------------------------------------------------------------------
    
        
    def choose_exit(self,idx):
        
        
        
        chosen_exit_idx = np.random.choice(a=self.idxs,p=self.tpm[idx])
        chosen_exit = self.exits[chosen_exit_idx]
        
        self.entrance_idx = idx
        self.exit_idx = chosen_exit_idx
        
        self.current_entrance = self.entrances[idx]
        self.current_exit = chosen_exit
        
        # NOTE: we do not have to link entrance and exit as we do in
        # stop street and traffic light objects. This is beacuse the cirle
        # follows some internal track of nodes from the entrance to the exit as
        # opposed to the entrance directly leading to some varying exit.
        
        return chosen_exit,chosen_exit_idx
        
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        sizing = {3:'small',5:'medium',7:'large'}
        return 'Circle: {0} ({1})'.format(sizing[self.size],
                                          hex(id(self)))

    
#------------------------------------------------------------------------------
    

    
        
    
