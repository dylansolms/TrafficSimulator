
import numpy as np

#from traffic_light_display import TrafficLightDisplay

#------------------------------------------------------------------------------



class TrafficLightCycle(object):
    
    '''
    Put this in the heap along with vehicles.
    Extract it from the heap at its start time to change the current cycle
    of the traffic light to the extacted cycle.
    '''
    
    def __init__(self,start_time,cycle_specs,traffic_light=None):
        self.time = start_time
        assert len(cycle_specs) == 5 # (duration,to_unlock,tpm,to_lock,display)
        self.cycle_specs = cycle_specs
        self.start_time = start_time
        self.end_time = start_time + cycle_specs[0]
        self.traffic_light = traffic_light
        self.is_cycle = True
        

    #--------------------------------------------------------------------------
    
    def activate(self):
        duration,to_unlock,tpm,to_lock,signal_specs = self.cycle_specs
        # Lock the entrances 
        self.traffic_light.lock(to_lock)
        self.traffic_light.unlock(to_unlock)
        self.traffic_light.tpm = tpm
#        self.traffic_light.unlock_time = self.end_time
        self.traffic_light.update_unlock_time(self.end_time)
        
        if self.traffic_light.display is not None :
            traffic_light_display = self.traffic_light.display
#            assert isinstance(traffic_light_display,TrafficLightDisplay)
            traffic_light_display.show_signals(signal_specs)
        return None        

    
    #--------------------------------------------------------------------------
    
    def __eq__(self,other):
        return self.time == other.time
    
    #--------------------------------------------------------------------------
    
    def __lt__(self,other):
        return self.time < other.time
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Traffic Light Cycle ({0})'.format(self.time)



#------------------------------------------------------------------------------

def N_S_flow(duration:float,
             prob_N_S:float,
             prob_S_N:float):
    
    '''
    Northern and Southern entrances allow traffic to flow forward and turn left.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last.
    prob_N_S: float
        The probability that a vehicle at the Northern entrance selects South
        as its exit (moves forward). With probability 1 - prob_N_S will a 
        vehicle then select East as its exit (left turn).
    prob_S_N: float
        The probability that a vehicle at the Southern entrance selects North
        as its exit (moves forward). With probability 1 - prob_S_N will a 
        vehicle then select West as its exit (left turn).
        
    Raises:
    -------
    AssertionError:
        Probability values are not valid.
    ValueError:
        duration must be positive and non-zero.
        
    Returns:
    ---------
    tuple: not relevant for user purposes.
    '''
    
    assert prob_N_S <= 1 and prob_N_S >= 0
    assert prob_S_N <= 1 and prob_S_N >= 0
    if duration <= 0:
        raise ValueError('We must have duration > 0 .')
    prob_N_E = 1 - prob_N_S
    prob_S_W = 1 - prob_S_N
    entrances = (0,2)
    to_lock = (1,3)
    tpm = np.zeros((4,4))
    tpm[0,2] = prob_N_S
    tpm[0,1] = prob_N_E
    tpm[2,0] = prob_S_N
    tpm[2,3] = prob_S_W
    
    
    display = [{'color':'green','message':'Go'},   # N
               {'color':'red','message':'Stop'},   # E
               {'color':'green','message':'Go'},   # S
               {'color':'red','message':'Stop'}]   # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def W_E_flow(duration:float,
             prob_W_E:float,
             prob_E_W:float):
    
    '''
    Western and Eastern entrances allow traffic to flow forward and turn left.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last.
    prob_W_E: float
        The probability that a vehicle at the Western entrance selects East
        as its exit (moves forward). With probability 1 - prob_W_E will a 
        vehicle then select North as its exit (left turn).
    prob_E_W: float
        The probability that a vehicle at the Eastern entrance selects West
        as its exit (moves forward). With probability 1 - prob_E_W will a 
        vehicle then select South as its exit (left turn).
        
    Raises:
    -------
    AssertionError:
        Probability values are not valid.
    ValueError:
        duration must be positive and non-zero.
        
    Returns:
    ---------
    tuple: not relevant for user purposes.
    '''
    if duration <= 0:
        raise ValueError('We must have duration > 0 .')
    assert prob_W_E <= 1 and prob_W_E >= 0
    assert prob_E_W <= 1 and prob_E_W >= 0
    prob_W_N = 1 - prob_W_E
    prob_E_S = 1 - prob_E_W
    entrances = (1,3)
    to_lock = (0,2)
    tpm = np.zeros((4,4))
    tpm[1,3] = prob_E_W
    tpm[1,2] = prob_E_S
    tpm[3,1] = prob_W_E
    tpm[3,0] = prob_W_N
    
    display = [{'color':'red','message':'Stop'},    # N
               {'color':'green','message':'Go'},    # E
               {'color':'red','message':'Stop'},    # S
               {'color':'green','message':'Go'}]    # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------



def N_S_overwash(duration:float):
    
    '''
    Northern entrance only flows to the Western exit.
    Southern entrance only flows to the Eastern exit.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last.
        
    Raises:
    -------
    ValueError:
        duration must be positive and non-zero.
        
    Returns:
    ---------
    tuple: not relevant for user purposes.
    '''
    if duration <= 0:
        raise ValueError('We must have duration > 0 .')
    entrances = (0,2)
    to_lock = (1,3)
    tpm = np.zeros((4,4))
    tpm[0,3] = 1
    tpm[2,1] = 1
    
    display = [{'color':'green','message':'-> only'},    # N
               {'color':'red','message':'Stop'},         # E
               {'color':'green','message':'-> only'},    # S
               {'color':'red','message':'Stop'}]         # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def W_E_overwash(duration:float):
    
    '''
    Eastern entrance only flows to the Northern exit.
    Western entrance only flows to the Southern exit.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last.
        
    Raises:
    -------
    ValueError:
        duration must be positive and non-zero.
        
    Returns:
    ---------
    tuple: not relevant for user purposes.
    '''
    if duration <= 0:
        raise ValueError('We must have duration > 0 .')
        
    entrances = (1,3)
    to_lock = (0,2)
    tpm = np.zeros((4,4))
    tpm[1,0] = 1
    tpm[3,2] = 1
    
    display = [{'color':'red','message':'Stop'},       # N
               {'color':'green','message':'-> only'},  # E
               {'color':'red','message':'Stop'},       # S
               {'color':'green','message':'-> only'}]  # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------




def N_flow(duration:float,
           prob_N_E:float,
           prob_N_S:float,
           prob_N_W:float):
    
    '''
    Only flow from the Northern entrance is permitted.
    It can flow to any of the other exits except North.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last.
    prob_N_E: float
        Left turn.
    prob_N_S: float
        Move forward.
    prob_N_W: float
        Right turn.
        
    Raises:
    -------
    AssertionError:
        Probability values are not valid.
    ValueError:
        duration must be positive and non-zero.
        
    Returns:
    ---------
    tuple: not relevant for user purposes.
    '''  
    if duration <= 0:
        raise ValueError('We must have duration > 0 .')
    assert prob_N_E + prob_N_S + prob_N_W == 1
    entrances = (0,)
    to_lock = (1,2,3)
    tpm = np.zeros((4,4))
    tpm[0,1] = prob_N_E  
    tpm[0,2] = prob_N_S
    tpm[0,3] = prob_N_W
    
    display = [{'color':'green','message':'Go ->'},    # N
               {'color':'red','message':'Stop'},       # E
               {'color':'red','message':'Stop'},       # S
               {'color':'red','message':'Stop'}]       # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def S_flow(duration:float,
           prob_S_W:float,
           prob_S_N:float,
           prob_S_E:float):
    
    '''
    Only flow from the Southern entrance is permitted.
    It can flow to any of the other exits except South.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last.
    prob_S_W: float
        Left turn.
    prob_S_N: float
        Move forward.
    prob_S_E: float
        Right turn.
        
    Raises:
    -------
    AssertionError:
        Probability values are not valid.
    ValueError:
        duration must be positive and non-zero.
        
    Returns:
    ---------
    tuple: not relevant for user purposes.
    '''   
    
    assert prob_S_W + prob_S_N + prob_S_E == 1
    if duration <= 0:
        raise ValueError('We must have duration > 0 .')

    entrances = (2,)
    to_lock = (0,1,3)
    tpm = np.zeros((4,4))
    tpm[2,0] = prob_S_N
    tpm[2,3] = prob_S_W
    tpm[2,1] = prob_S_E
    
    display = [{'color':'red','message':'Stop'},       # N
               {'color':'red','message':'Stop'},       # E
               {'color':'green','message':'Go ->'},    # S
               {'color':'red','message':'Stop'}]       # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def E_flow(duration:float,
           prob_E_S:float,
           prob_E_W:float,
           prob_E_N:float):
    
    '''
    Only flow from the Eastern entrance is permitted.
    It can flow to any of the other exits except East.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last.
    prob_E_S: float
        Left turn.
    prob_E_W: float
        Move forward.
    prob_E_N: float
        Right turn.
        
    Raises:
    -------
    AssertionError:
        Probability values are not valid.
    ValueError:
        duration must be positive and non-zero.
        
    Returns:
    ---------
    tuple: not relevant for user purposes.
    '''   
    
    assert prob_E_N + prob_E_S + prob_E_W == 1

    if duration <= 0:
        raise ValueError('We must have duration > 0 .')
    entrances = (1,)
    to_lock = (0,2,3)
    tpm = np.zeros((4,4))
    tpm[1,2] = prob_E_S
    tpm[1,3] = prob_E_W
    tpm[1,0] = prob_E_N
    
    display = [{'color':'red','message':'Stop'},       # N
               {'color':'green','message':'Go ->'},    # E
               {'color':'red','message':'Stop'},       # S
               {'color':'red','message':'Stop'}]       # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def W_flow(duration:float,
           prob_W_N:float,
           prob_W_E:float,
           prob_W_S:float):
    
    '''
    Only flow from the Eastern entrance is permitted.
    It can flow to any of the other exits except East.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last.
    prob_W_N: float
        Left turn.
    prob_W_E: float
        Move forward.
    prob_W_S: float
        Right turn.
        
    Raises:
    -------
    AssertionError:
        Probability values are not valid.
    ValueError:
        duration must be positive and non-zero.
        
    Returns:
    ---------
    tuple: not relevant for user purposes.
    '''  
    if duration <= 0:
        raise ValueError('We must have duration > 0 .')
    assert prob_W_N + prob_W_E + prob_W_S

    entrances = (3,)
    to_lock = (0,1,2)
    tpm = np.zeros((4,4))
    tpm[3,0] = prob_W_N
    tpm[3,1] = prob_W_E
    tpm[3,2] = prob_W_S
    
    display = [{'color':'red','message':'Stop'},       # N
               {'color':'red','message':'Stop'},       # E
               {'color':'red','message':'Stop'},       # S
               {'color':'green','message':'Go ->'}]    # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


default_cycle = [
                 N_flow(10,0.2,0.6,0.2),
                 N_S_flow(15,0.8,0.8),
                 N_S_overwash(5),
                 S_flow(10,0.2,0.6,0.2),
                 E_flow(10,0.2,0.6,0.2),
                 W_E_flow(15,0.8,0.8),
                 W_E_overwash(5),
                 W_flow(10,0.2,0.6,0.2)
                 ]

#------------------------------------------------------------------------------




























#------------------------------------------------------------------------------