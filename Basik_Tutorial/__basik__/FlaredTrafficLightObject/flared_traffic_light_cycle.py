


from ..utils import dict_to_array,check_tpm


#------------------------------------------------------------------------------

default_probs = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
                 'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
                 'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
                 'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}

#------------------------------------------------------------------------------

default_tpm = dict_to_array(default_probs)

#------------------------------------------------------------------------------

class FlaredTrafficLightCycle(object):
    
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
        print('Calling activate()...')
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
        print('...calling complete')
        return None        

    
    #--------------------------------------------------------------------------
    
    def __eq__(self,other):
        return self.time == other.time
    
    #--------------------------------------------------------------------------
    
    def __lt__(self,other):
        return self.time < other.time
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Flared Traffic Light Cycle ({0})'.format(self.time)



#------------------------------------------------------------------------------

def N_S_flow(duration,tpm=default_tpm):
    
    '''
    Northern and Southern entrances allow traffic to flow forward and 
    turn left. This means that only the left buffers of active entrances can
    empty its vehicle content.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last i.e. how long the signal will last.
    tpm: dict or numpy.ndarray
        This dictates the dynamic/choices that occurs when vehicles move from a
        lane/road object onto a flared traffic light and have to decide on which
        buffer to choose. Keep in mind, a vehicle that wants to proceed forward
        or turn left will keep to the left (main) buffer while a vehicle that
        would like to turn right will move into the right buffer and wait their
        until the arrow signal for allowing right turns appears.
        Dictionary format: 
        >>> tpm = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
        ...        'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
        ...        'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
        ...        'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}
        Numpy array example:
        >>> tpm = numpy.array([[0,0.25,0.5,0.25],
        ...                    [0.25,0,0.25,0.5],
        ...                    [0.5,0.25,0,0.25],
        ...                    [0.25,0.5,0.25,0]])
    
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
    tpm = check_tpm(tpm)

    entrances = (0,2)
    to_lock = (1,3)
    display = [{'color':'green','message':'Go'},   # N
               {'color':'red','message':'Stop'},   # E
               {'color':'green','message':'Go'},   # S
               {'color':'red','message':'Stop'}]   # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def W_E_flow(duration,tpm=default_tpm):
    
    '''
    Western and Eastern entrances allow traffic to flow forward and turn
    left. This means that only the left buffers of active entrances can
    empty its vehicle content.
    
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last i.e. how long the signal will last.
    tpm: dict or numpy.ndarray
        This dictates the dynamic/choices that occurs when vehicles move from a
        lane/road object onto a flared traffic light and have to decide on which
        buffer to choose. Keep in mind, a vehicle that wants to proceed forward
        or turn left will keep to the left (main) buffer while a vehicle that
        would like to turn right will move into the right buffer and wait their
        until the arrow signal for allowing right turns appears.
        Dictionary format: 
        >>> tpm = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
        ...        'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
        ...        'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
        ...        'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}
        Numpy array example:
        >>> tpm = numpy.array([[0,0.25,0.5,0.25],
        ...                    [0.25,0,0.25,0.5],
        ...                    [0.5,0.25,0,0.25],
        ...                    [0.25,0.5,0.25,0]])
    
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
    tpm = check_tpm(tpm)
    
    entrances = (1,3)
    to_lock = (0,2)
    
    display = [{'color':'red','message':'Stop'},    # N
               {'color':'green','message':'Go'},    # E
               {'color':'red','message':'Stop'},    # S
               {'color':'green','message':'Go'}]    # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------



def N_S_overwash(duration,tpm=default_tpm):
    
    '''
    Northern entrance only flows to the Western exit.
    Southern entrance only flows to the Eastern exit.
    Only right buffers empty their vehicle content as a result.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last i.e. how long the signal will last.
    tpm: dict or numpy.ndarray
        This dictates the dynamic/choices that occurs when vehicles move from a
        lane/road object onto a flared traffic light and have to decide on which
        buffer to choose. Keep in mind, a vehicle that wants to proceed forward
        or turn left will keep to the left (main) buffer while a vehicle that
        would like to turn right will move into the right buffer and wait their
        until the arrow signal for allowing right turns appears.
        Dictionary format: 
        >>> tpm = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
        ...        'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
        ...        'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
        ...        'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}
        Numpy array example:
        >>> tpm = numpy.array([[0,0.25,0.5,0.25],
        ...                    [0.25,0,0.25,0.5],
        ...                    [0.5,0.25,0,0.25],
        ...                    [0.25,0.5,0.25,0]])
    
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
    tpm = check_tpm(tpm)
    
    entrances = (0,2)
    to_lock = (1,3)

    display = [{'color':'green','message':'-> only'},    # N
               {'color':'red','message':'Stop'},         # E
               {'color':'green','message':'-> only'},    # S
               {'color':'red','message':'Stop'}]         # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def W_E_overwash(duration,tpm=default_tpm):
    
    '''
    Eastern entrance only flows to the Northern exit.
    Western entrance only flows to the Southern exit.
    Only right buffers empty their vehicle content as a result.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last i.e. how long the signal will last.
    tpm: dict or numpy.ndarray
        This dictates the dynamic/choices that occurs when vehicles move from a
        lane/road object onto a flared traffic light and have to decide on which
        buffer to choose. Keep in mind, a vehicle that wants to proceed forward
        or turn left will keep to the left (main) buffer while a vehicle that
        would like to turn right will move into the right buffer and wait their
        until the arrow signal for allowing right turns appears.
        Dictionary format: 
        >>> tpm = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
        ...        'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
        ...        'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
        ...        'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}
        Numpy array example:
        >>> tpm = numpy.array([[0,0.25,0.5,0.25],
        ...                    [0.25,0,0.25,0.5],
        ...                    [0.5,0.25,0,0.25],
        ...                    [0.25,0.5,0.25,0]])
    
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
    tpm = check_tpm(tpm)
    
    entrances = (1,3)
    to_lock = (0,2)


    display = [{'color':'red','message':'Stop'},       # N
               {'color':'green','message':'-> only'},  # E
               {'color':'red','message':'Stop'},       # S
               {'color':'green','message':'-> only'}]  # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


 
def N_flow(duration,tpm=default_tpm):
    
    '''
    Only flow from the Northern entrance is permitted.
    It can flow to any of the other exits except North.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last i.e. how long the signal will last.
    tpm: dict or numpy.ndarray
        This dictates the dynamic/choices that occurs when vehicles move from a
        lane/road object onto a flared traffic light and have to decide on which
        buffer to choose. Keep in mind, a vehicle that wants to proceed forward
        or turn left will keep to the left (main) buffer while a vehicle that
        would like to turn right will move into the right buffer and wait their
        until the arrow signal for allowing right turns appears.
        Dictionary format: 
        >>> tpm = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
        ...        'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
        ...        'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
        ...        'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}
        Numpy array example:
        >>> tpm = numpy.array([[0,0.25,0.5,0.25],
        ...                    [0.25,0,0.25,0.5],
        ...                    [0.5,0.25,0,0.25],
        ...                    [0.25,0.5,0.25,0]])
    
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
    tpm = check_tpm(tpm)
    
    entrances = (0,)
    to_lock = (1,2,3)

    
    display = [{'color':'green','message':'Go ->'},    # N
               {'color':'red','message':'Stop'},       # E
               {'color':'red','message':'Stop'},       # S
               {'color':'red','message':'Stop'}]       # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def S_flow(duration,tpm=default_tpm):
    
    '''
    Only flow from the Southern entrance is permitted.
    It can flow to any of the other exits except South.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last i.e. how long the signal will last.
    tpm: dict or numpy.ndarray
        This dictates the dynamic/choices that occurs when vehicles move from a
        lane/road object onto a flared traffic light and have to decide on which
        buffer to choose. Keep in mind, a vehicle that wants to proceed forward
        or turn left will keep to the left (main) buffer while a vehicle that
        would like to turn right will move into the right buffer and wait their
        until the arrow signal for allowing right turns appears.
        Dictionary format: 
        >>> tpm = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
        ...        'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
        ...        'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
        ...        'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}
        Numpy array example:
        >>> tpm = numpy.array([[0,0.25,0.5,0.25],
        ...                    [0.25,0,0.25,0.5],
        ...                    [0.5,0.25,0,0.25],
        ...                    [0.25,0.5,0.25,0]])
    
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
    tpm = check_tpm(tpm)
    
    entrances = (2,)
    to_lock = (0,1,3)

    
    display = [{'color':'red','message':'Stop'},       # N
               {'color':'red','message':'Stop'},       # E
               {'color':'green','message':'Go ->'},    # S
               {'color':'red','message':'Stop'}]       # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def E_flow(duration,tpm=default_tpm):
    
    '''
    Only flow from the Eastern entrance is permitted.
    It can flow to any of the other exits except East.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last i.e. how long the signal will last.
    tpm: dict or numpy.ndarray
        This dictates the dynamic/choices that occurs when vehicles move from a
        lane/road object onto a flared traffic light and have to decide on which
        buffer to choose. Keep in mind, a vehicle that wants to proceed forward
        or turn left will keep to the left (main) buffer while a vehicle that
        would like to turn right will move into the right buffer and wait their
        until the arrow signal for allowing right turns appears.
        Dictionary format: 
        >>> tpm = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
        ...        'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
        ...        'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
        ...        'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}
        Numpy array example:
        >>> tpm = numpy.array([[0,0.25,0.5,0.25],
        ...                    [0.25,0,0.25,0.5],
        ...                    [0.5,0.25,0,0.25],
        ...                    [0.25,0.5,0.25,0]])
    
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
    tpm = check_tpm(tpm)
    
    entrances = (1,)
    to_lock = (0,2,3)

    
    display = [{'color':'red','message':'Stop'},       # N
               {'color':'green','message':'Go ->'},    # E
               {'color':'red','message':'Stop'},       # S
               {'color':'red','message':'Stop'}]       # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


def W_flow(duration,tpm=default_tpm):
    
    '''
    Only flow from the Eastern entrance is permitted.
    It can flow to any of the other exits except East.
    
    Parameters:
    -----------
    duration: float
        A value in seconds of how long this state of the traffic light will
        last i.e. how long the signal will last.
    tpm: dict or numpy.ndarray
        This dictates the dynamic/choices that occurs when vehicles move from a
        lane/road object onto a flared traffic light and have to decide on which
        buffer to choose. Keep in mind, a vehicle that wants to proceed forward
        or turn left will keep to the left (main) buffer while a vehicle that
        would like to turn right will move into the right buffer and wait their
        until the arrow signal for allowing right turns appears.
        Dictionary format: 
        >>> tpm = {'N':{'N':0,'E':0.25,'S':0.5,'W':0.25},
        ...        'E':{'N':0.25,'E':0,'S':0.25,'W':0.5},
        ...        'S':{'N':0.5,'E':0.25,'S':0,'W':0.25},
        ...        'W':{'N':0.25,'E':0.5,'S':0.25,'W':0}}
        Numpy array example:
        >>> tpm = numpy.array([[0,0.25,0.5,0.25],
        ...                    [0.25,0,0.25,0.5],
        ...                    [0.5,0.25,0,0.25],
        ...                    [0.25,0.5,0.25,0]])
    
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
    tpm = check_tpm(tpm)
    
    entrances = (3,)
    to_lock = (0,1,2)

    
    display = [{'color':'red','message':'Stop'},       # N
               {'color':'red','message':'Stop'},       # E
               {'color':'red','message':'Stop'},       # S
               {'color':'green','message':'Go ->'}]    # W
    
    return duration,entrances,tpm,to_lock,display

#------------------------------------------------------------------------------


default_cycle = [
                 N_flow(10),
                 N_S_flow(15),
                 N_S_overwash(5),
                 S_flow(10),
                 E_flow(10),
                 W_E_flow(15),
                 W_E_overwash(5),
                 W_flow(10)
                 ]

#------------------------------------------------------------------------------




























#------------------------------------------------------------------------------