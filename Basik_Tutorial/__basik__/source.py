
import numpy as np
import matplotlib.pyplot as plt
from .VehicleObject import Vehicle,color_list
from .node import Node
from .utils import cycle_list,merge_dicts,get_pi,get_ordered_dict
from collections import OrderedDict
from pandas import read_csv
import warnings
try:
    import cPickle as pickle
except ImportError or ModuleNotFoundError:
    import pickle

#-------------------------------------------------------------------------------

__all__ = ['Rate','Source','source_count','MMPP_rate_schedule']


#-------------------------------------------------------------------------------


def csv_to_source(file_name:str,
                  vehicle_velocity:'float m/s',
                  target_node:'__basik__.node.Node',
                  vehicle_color:str='random',
                  record_movement:bool=False):
        
    '''Converts a csv file to a __basik__.source.Source object.
    
    The csv file should contain time-stamps and not intervals.
    
    Parameters:
    -----------
    file_name: str
        A working path name. If a .csv extension is not present then one will
        be added. The user will be notified of this via a warning produced from
        the warnings module.
    vehicle_velocity: float
        A value in meters per second. All vehicle will move at this
        velocity on average.
    target_node: __basik__.node.Node
        The node at which new vehicles will arrive/appear/be introduced to
        interact in the simulation.
    vehicle_color: str
        This is the color setting of the vehicle. Note that if the color has
        been set to 'random' then the randomly selected color can be accessed
        via Vehicle.vehicle_display.color
    record_movement: bool
        A vehicle can be produced by the source with the setting/instructions
        that it record its movement across the simulation. A recorded vehicle
        can then be probed for this information from the vehicles list.
            
    Raises:
    -------
    AssetionError:
        If the target_node is not an instance of __basik__.node.Node
    ValuError:
        If a csv file is presented that has no header 'time-stamps'.
        
    Returns:
    --------
    __basik__.source.Source
    '''
    
    
    if file_name[-4:] != '.csv':
            file_name += '.csv'
            warnings.warn('.csv extension was added.')
    
    rate_schedule = {0:file_name}
    
    assert isinstance(target_node,Node)
                
    source = Source(vehicle_velocity=vehicle_velocity,
                    target_node=target_node,
                    rate_schedule=rate_schedule,
                    vehicle_color=vehicle_color,
                    record_movement=record_movement)
    
    return source
    
    
#------------------------------------------------------------------------------


def pickle_to_source(file_name:str,
                  vehicle_velocity:'float m/s',
                  target_node:'__basik__.node.Node',
                  vehicle_color:str='random',
                  record_movement:bool=False):
        
    '''Converts a pickled (serialised) __basik__.record.Record object
    to a __basik__.source.Source object.
    
    
    Parameters:
    -----------
    file_name: str
        A working path name. If a .pkl extension is not present then one will
        be added. The user will be notified of this via a warning produced from
        the warnings module.
    vehicle_velocity: float
        A value in meters per second. All vehicle will move at this
        velocity on average.
    target_node: __basik__.node.Node
        The node at which new vehicles will arrive/appear/be introduced to
        interact in the simulation.
    vehicle_color: str
        This is the color setting of the vehicle. Note that if the color has
        been set to 'random' then the randomly selected color can be accessed
        via Vehicle.vehicle_display.color
    record_movement: bool
        A vehicle can be produced by the source with the setting/instructions
        that it record its movement across the simulation. A recorded vehicle
        can then be probed for this information from the vehicles list.
            
    Raises:
    -------
    AssetionError:
        If the target_node is not an instance of __basik__.node.Node
        
    Returns:
    --------
    __basik__.source.Source
    '''
    
    
    if file_name[-4:] != '.pkl':
            file_name += '.pkl'
            warnings.warn('.pkl extension was added.')
    
    rate_schedule = {0:file_name}
    
    assert isinstance(target_node,Node)
                
    source = Source(vehicle_velocity=vehicle_velocity,
                    target_node=target_node,
                    rate_schedule=rate_schedule,
                    vehicle_color=vehicle_color,
                    record_movement=record_movement)
    
    return source

#-------------------------------------------------------------------------------


def general_function(t,
                     constant,
                     drift,
                     drift_reference,
                     amplitude,
                     prob,
                     T1,
                     T2):
    
    return constant + (t-drift_reference)*drift +\
           amplitude*( prob*np.sin(t*np.pi/T1) +\
           (1-prob)*np.cos(t*np.pi/T2))

#-------------------------------------------------------------------------------



def MMPP_rate_schedule(Q:'array(N,N)',
                       Rates:'array(N)',
                       end_time:float,
                       start_time:float=0,
                       pi:'array(N)'=None):
    
    '''Creates an ordered dictionary of rate schedules. This rate schedule
    will allow the source object to simulate a Markov Modulated Poisson 
    Process (MMPP).
    
    Parameters:
    -----------
    Q: numpy.ndarray (N,N)
        A Generator Matrix.
    Rates: numpy.ndarray (N,)
        An array of Poisson Arrival Rates.
    end_time: float
        The total duration for which a MMPP schedule exists.
    start_time:
        At what time the MMPP schedule starts to exist.
    pi: np.ndarray(N,) or None
        The probability distribution vector for the starting states. If None is
        given then the stationary distribution of the embedded chain of the
        Generator Matrix will be used.
        
    Returns:
    --------
    collection.OrderedDict
        This will be a rates schedule that can be fed into a 
        __basik__.source.Source object.
        
    Raises:
    -------
    ValueError
        If the Generator Matrix given does not adhere to required properties.
        
    Notes:
    -------
    For a bried tutorial on MMPP see:
    https://pdfs.semanticscholar.org/92c3/bc62686c65765bf8596850033438b46413f8.pdf
    
    '''
    
    assert end_time > start_time
    
    # SOURCE:
    # https://en.wikipedia.org/wiki/Markov_chain#Embedded_Markov_chain
    
    N = len(Rates)
    
    
    message = 'The absolute value of the diagonals of Q must equal the sum '+\
              'of the off-diagonal elements in the row which it inhabits.'
    
    # Setup the embedded Markov Chain
    P = np.zeros((N,N))
    
    for i in range(N):
        
        # First, get the sampling rate of each row. Assert that the 
        # given generator has been properly formulated.
        
        diag_element = None
        sampling_rate = 0
        
        for j in range(N):
            
            if i == j:
                diag_element = Q[i,j]
                continue
            
            sampling_rate += Q[i,j]
            
        if abs(diag_element) != sampling_rate:
            raise ValueError(message)
        
        # Second, create the actual embedded chain.
            
        for j in range(N):
            
            if i == j:
                continue
            
            P[i,j] = Q[i,j]/sampling_rate
        
    if pi is None:
        # We the compute the stationary distribution.
        pi = get_pi(P)
    
    else:
        pi = np.array(pi)  # ensure it is a numpy array
        
    # We can now start the simulation of the Continuous-time Markov Process
    # via its embedded Markov Chain.
    
    # NOTE: we are simply setting up a rate shedule that would be
    # equivalent to a MMPP. We aren't simulating an actuall MMPP but just its
    # rate intensitiy. Its rate intensity is a Continuous-time Markov Process.
    
    rate_schedules = []  # These will all be merged into and OrderedDict.
    # This dictionary will resemble the required rate_schedule form.
    
    t = start_time
    T = end_time
    
    states = np.arange(N,dtype=int)
    current_state = np.random.choice(states,p=pi)
    
    
    while True:
        
        rate = Rates[current_state]
        next_state = np.random.choice(states,p=P[current_state])
        transition_rate = Q[current_state,next_state]
        duration = np.random.exponential(scale=1./transition_rate)
        
        t += duration
        
        piece_wise_constant_rate = Rate(constant=rate)
        
        rate_schedules.append({t:piece_wise_constant_rate})
        
        if t >= T:
            break
        
        current_state = next_state
        
    # Create one single ordered dictionary.
    mmpp_schedule = merge_dicts(*rate_schedules,
                                ordered=True,
                                ignore_duplicates=True)
    
    return mmpp_schedule
        

#-------------------------------------------------------------------------------


class Rate(object):
    
    '''Produces a callable object from the give parameters.
    
    The intention of this callable object is to produce some custom rate 
    intensity that a source object can use to simulate arrivals from.
    Note that we are modelling the rate intensity of an Exponential process.
    An example of a rate schedule using Rate objects could be as follows:
    >>> schedule = {10:Rate(constant=1),20:Rate(constant=1,drift=0.1)}
    A preferred version would actually be as follows:
    >>> schedule = collections.OrderedDict(
    ...                                    {10:Rate(constant=1),
    ...                                     20:Rate(constant=1,drift=0.1)}
    ...                                    )
    
    Notes:
    -------
    The rate intensity function of the Exponential process is modelled as follows:
    ..math:: \lambda(t) = c + (t-t_0)\mu + A(p \sin(\frac{t\pi}{T_1}) + (1-p)\cos(\frac{t\pi}{T_2}))
    
    '''


    
    def __init__(self,constant:float,
                      drift=None,
                      drift_reference=None,
                      amplitude=None,
                      prob=None,
                      T1=None,
                      T2=None):
        
        '''We will provide parameters for the callable function.
        
        We are modelling:
        
        rate(t) = constant + (t-drift_reference)*drift +
                  amplitude*( prob*np.sin(t*np.pi/T1) +
                  (1-prob)*np.cos(t*np.pi/T2))
        
        Parameters:
        -----------
        constant: float
            Time-independent parameter.
        drift: float or None
            Linear change with time.
            Setting to None is equivalent to setting it to zero.
        drift_reference: float or None
            Some reference point in time from which we add drift. If time is
            larger than the reference point we add the drift value. When it is
            smaller we subtract the value. This reference value need not be 
            positive. Setting to None is equivalent to setting it to zero.
        amplitude: float or None
            Amplitude of periodic oscillations. 
            Setting to None is equivalent to setting it to zero.
        prob: float or None
            A value between zero and one. This dictates how much the amplitude
            is attributed to the sine wave.
            Setting to None is equivalent to setting it to zero.
        T1: float or None
            The period of the sine wave.
            Setting to None is equivalent to setting it to pi.
        T2: float or None
            The period of the cosine wave.
            Setting to None is equivalent to setting it to pi.
            
        Raises:
        -------
        AssetionError:
            If prob is not between zero and one.
        
        '''
        
        if drift is None:
            drift = 0
        if drift_reference is None:
            drift_reference = 0
        if amplitude is None:
            amplitude = 0
        if prob is None:
            prob = 0
        if T1 is None:
            T1 = np.pi
        if T2 is None:
            T2 = np.pi
        
        assert prob >=0 and prob <= 1
            
        self.constant = constant
        self.drift = drift
        self.drift_reference = drift_reference
        self.amplitude = amplitude
        self.prob = prob
        self.T1 = T1
        self.T2 = T2
        
    def __call__(self,t:float):
        
        '''
        Parameters:
        -----------
        t: float
            The independent variable time.
        
        Retruns:
        --------
        __basik__.source.general_function
        i.e. rate(t) = constant + (t-drift_reference)*drift +
                       amplitude*( prob*np.sin(t*np.pi/T1) +
                       (1-prob)*np.cos(t*np.pi/T2))
        '''
        
        return general_function(t,
                            self.constant,
                            self.drift,
                            self.drift_reference,
                            self.amplitude,
                            self.prob,
                            self.T1,
                            self.T2)
        


    
#-------------------------------------------------------------------------------

source_count = 0


def reset_source_count(count=0):
    '''Sets the source count to the value required.
    '''
    assert isinstance(count,int)
    assert count >= 0
    globals()['source_count'] = 0
#    global source_count
#    source_count = 0
    return None
    

#-------------------------------------------------------------------------------


class Source(object):
    '''Introduces new vehicles into the simulation.
    
    
    Attributes:
    -----------
    ID: int
        Every source is assigned an integer starting at 0 (Natural Number).
        Vehicles produced by thus source will contain the ID as well. This way
        one can track from which source vehicles were produced at a given
        recorded node.
    arrival_times: list
        This attribute only exists if the setup_arrivals is called. It provided
        a list of the ideal arrival times of vehicles to be produced by the 
        source. By ideal, we refer to the fact that if a source is blocked by
        a vehicle at one of the scheduled arrival times then it will be delayed.
        This due to the calibrate_forward method in 
        __basik__.VehicleObjects.vehicle.Vehicle.
    current_time: float
        This attribute only exists if the setup_arrivals is called. It is the
        last time that a source produced an arrival.
    figure: matplotlib.figure.Figure or bool 
        Only exists if the view_rate method is called. If an existing axes
        is provided in the arguments of view_rate then no new figure will
        be generated and figure will be set to True. Otherwise, a new
        figure will be generated.
    axes: matplotlib.axes._subplots.AxesSubplot
        Only exists if the view_rate method is called. If no axes is provided 
        then a new axes for the plot (along with a new figure) will be
        produced.
    '''
    
    
    SOURCE = True
    
    size = 1
    
    #---------------------------------------------------------------------------
    
    def __init__(self,vehicle_velocity:float,
                      target_node:'Node',
                      rate_schedule:'dict -> {end_time:rate(args)}',
                      vehicle_color='random',
                      record_movement=False):
        
        '''
        Parameters:
        -----------
        vehicle_velocity: float
            A value in meters per second. All vehicle will move at this
            velocity on average.
        target_node: __basik__.node.Node
            The node at which new vehicles will arrive/appear/be introduced to
            interact in the simulation.
        rate_schedule: dict or collections.OrderedDict (preferred)
            This is a dictionary that contains piece-wise defined rate intensity
            functions for an Exponential process to simulate vehicle arrivals
            from. The form of a rate scedule is:
            >>> schedule = {end time of schedule:__basik__.source.Rate}
            We assume the start time of a Rate function to the end time of the
            schedule before that. In the case of the first Rate function its 
            start time is that defined by the arguments in the setup_arrivals
            method. This start time is usually zero (by default) but it need not
            be so. 
        vehicle_color: str
            This is the color setting of the vehicle. Note that if the color has
            been set to 'random' then the randomly selected color can be accessed
            via Vehicle.vehicle_display.color
        record_movement: bool
            A vehicle can be produced by the source with the setting/instructions
            that it record its movement across the simulation. A recorded vehicle
            can then be probed for this information from the vehicles list.
                
        Raises:
        -------
        AssetionError:
            If the target_node is not an instance of __basik__.node.Node
            
        Returns:
        --------
        None
        
        
        Example:
        --------
        We present three examples of valid rate schedules.
        
        Example 1: Using __basik__.source.Rate
        >>> schedule = {10:Rate(constant=1),20:Rate(constant=1,drift=0.1)}
        A preferred version would actually be as follows:
        >>> schedule = collections.OrderedDict(
        ...                                    {10:Rate(constant=1),
        ...                                     20:Rate(constant=1,drift=0.1)}
        ...                                    )
        
        Example 2: using a csv file
        >>> schedule = {0:'/some_valid_path_name.csv'}
        We put the end time here as zero. It could be anything though in this
        case as we are not going to simulate from a piecewise Exponential rate
        intensity. All the information necessitated is found in the csv file.
        It is important to note that the header of the csv file must be
        'time-stamps' and that only one file can be given.
        
        Example 3: using a pickled/serialised __basik__.record.Record object
        >>> schedule = {0:'/some_valid_path_name.pkl'}
        The same arguments hold as in Example 2. Ensure that the serialised 
        object does indeed contain recorded vehicles.
        
        See Also:
        ----------
        __basik__.source.Rate
        __basik__.source.Source.setup_arrivals
        '''
        
        
        self.vehicle_velocity = vehicle_velocity
        self.target_node = target_node
        target_node.source_attached = True
        target_node.source = self
        
        if not isinstance(rate_schedule,OrderedDict):
            rate_schedule = get_ordered_dict(rate_schedule)
        self.rate_schedule = rate_schedule
        self.schedule_end_times = np.sort(np.array(list(rate_schedule.keys())))
        
        global source_count
        self.ID = source_count
        source_count += 1
        
        if vehicle_color not in color_list:
            string = 'Please chose one of the colors:'+\
            '\n{0}'.format(color_list)
            raise Exception(string)
        self.vehicle_color = vehicle_color
        
        self.record_movement = record_movement
        
    
    #---------------------------------------------------------------------------
        
    def _choose_rate_from_schedule(self,t):
        times = t - self.schedule_end_times
        times = np.array(times,dtype=object)
        times[times<0] = np.inf
        idx = np.argmin(times)
        schedule_time = self.schedule_end_times[idx]
        return self.rate_schedule[schedule_time]
        
    #---------------------------------------------------------------------------
        
    def _get_rate(self,t):
        rate_func = self._choose_rate_from_schedule(t)
        return rate_func(t)
        
    #---------------------------------------------------------------------------
    
    
    # OPTION 1: we simulate unique arrivals
    def _simulate_arrivals(self,end_time,start_time=0):
        
        '''
        This is done for a schedule of rates.
        '''
        
        T = end_time
        t = start_time
        
        self.arrival_times = []
        t = 0
        
        while True:
            
            
            rate = self._get_rate(t)
            if rate <= 0:
                rate = 5e-2  # some hard-coded minimum
            t += np.random.exponential(scale=1/rate)
            if t > T:
                break
            self.arrival_times.append(t)
            
            # Create a temp node that leads to the target node
            temp_node = Node(front=self.target_node)
            # We can store the arrival here
            # MAIN REASON for temp node:
            # If the target node is not available at the time of arrival 
            # (a very unlikely event) then the arrival can be delayed by 
            # remaining in its temp node for some time.            
        
            vehicle = Vehicle(velocity=self.vehicle_velocity,
                              global_time=t,
                              current_node=temp_node,
                              source_ID=self.ID,
                              color=self.vehicle_color,
                              record_movement=self.record_movement)
                              
            temp_node.occupied = True
            temp_node.vehicle = vehicle

            # Schedule an arrival  
            
            vehicle.schedule_move()
            # schedule_move() puts the vehicles into the Queue
#            Queue.push(vehicle)
            

        return None
    
    
    #---------------------------------------------------------------------------
    
    # OPTION 2: We read arrivals from a csv file.
    def _read_arrivals(self,file_name,
                            end_time=np.inf,# convert/read all
                            start_time=0):
        
        DataFrame = read_csv(file_name)
        column_name = list(DataFrame.columns)
        if 'time-stamps' not in column_name:
            message = '\'time-stamps\' must be a column name. '+\
                      'This way, the simulator knows that the data is not '+\
                      'intervals.'
            raise ValueError(message)
        
        time_stamps = DataFrame['time-stamps'].values.ravel()
        time_stamps.sort()  # just in case.
        
        original_start_time = time_stamps[0]
        # original_start_time + delta = start_time
        delta = start_time - original_start_time
        
        time_stamps += delta # Corrected
        
        self.arrival_times = []
        
        for t in time_stamps:
            
            if t > end_time:
                break
            
            self.arrival_times.append(t)
            
            temp_node = Node(front=self.target_node) 
    
            vehicle = Vehicle(velocity=self.vehicle_velocity,
                              global_time=t,
                              current_node=temp_node,
                              source_ID=self.ID,
                              color=self.vehicle_color,
                              record_movement=self.record_movement)
                              
            temp_node.occupied = True
            temp_node.vehicle = vehicle
            # Schedule an arrival  
            vehicle.schedule_move()
            
        return None
            

    #---------------------------------------------------------------------------
    
    # OPTION 3: We unpickle a Record object.
    def _unpickle_arrivals(self,file_name,
                                end_time=np.inf,
                                start_time=0):
        
        with open(file_name,'rb') as file:
            record = pickle.load(file)
            
        if not hasattr(record,'RECORD'):
            message = 'The pickled object is not a single Record object.'
            raise Exception(message)
            
        self._convert_record_object_to_arrivals(record,start_time=start_time)
        
        return None
    
    #---------------------------------------------------------------------------
    
    def _convert_record_object_to_arrivals(self,record,
                                                end_time=np.inf, # convert/read all
                                                start_time=0):
        

        if not bool(record.time_stamps):
            # If the record has no time-stamps first see if the record has not
            # been processed yet.
            # If the record object has recorded nothing then it will raise
            # an error itself/
            record.process_records()
            
        if not bool(record.time_stamps):
            # still empty
            message = 'No records were placed. Hence, there are no arrivals '+\
                      'to be generated.'
            warnings.warn(message)
            return None
            

        time_stamps = np.array(record.time_stamps)
        time_stamps.sort()  # just in case.
        
        original_start_time = time_stamps[0]
        # original_start_time + delta = start_time
        delta = start_time - original_start_time
        
        time_stamps += delta # Corrected
        
        self.arrival_times = []

        
        for t in time_stamps:
            
            if t > end_time:
                break
            
            self.arrival_times.append(t)
            
            temp_node = Node(front=self.target_node) 
    
            vehicle = Vehicle(velocity=self.vehicle_velocity,
                              global_time=t,
                              current_node=temp_node,
                              source_ID=self.ID,
                              color=self.vehicle_color,
                              record_movement=self.record_movement)
                              
            temp_node.occupied = True
            temp_node.vehicle = vehicle
            # Schedule an arrival  
            vehicle.schedule_move()
            
        return None
    
    #---------------------------------------------------------------------------
    
    
    def setup_arrivals(self,end_time,
                            start_time=0):
        
        '''Produces vehicle arrivals.
        
        This method will either:
            1) Simulate from a rate schedule,
            2) Read arrivals from a csv file
            3) Extract recorded vehicles from a serialised/pickled
               __basik__.record.Record object.
        
        In all three cases, vehicles will be produced and placed into the 
        current global queue.
        
        Parameters:
        -----------
        end_time: float
            The time at which the simulation will end. This must be larger than
            start_time. It can be larger than the largest end time in the
            rate_schedule. This just means that it will continue to use the last
            defined __basik__.rate.Rate object. In the case of a csv or pkl then
            no more arrivals will be produced. It is reommended that the end_time
            be chosen smaller that the maximum end time in a rate schedule as
            to allow the source to produce arrivals throughout the simulation.
        start_time: float
            The time at which the source will start to produce arrivals.
            
        Raises:
        -------
        AsserionError
            If end_time is not greater than start_time
        ValueError
            If the rate_schedule does not contain either a csv or pkl filepath
            or valid __basik__.rate.Rate objects.
            
        Returns:
        --------
        None
        
        '''
        
        
        assert end_time > start_time
        
        # A) a single item
        if len(self.rate_schedule) == 1:
            # It can be a single Rate object, a .csv file name or a
            # .pkl (pickle) file name. 
            item = list(self.rate_schedule.values())[0]
            
            # 1) Rate Objects
            if isinstance(item,Rate):
                self._simulate_arrivals(end_time,start_time)
            
            # 2) A file
            elif isinstance(item,str):
                
                extension = item[-4:]
                
                # 2a) A comma separated value file
                if extension == '.csv':
                    self._read_arrivals(file_name=item,
                                        end_time=end_time,
                                        start_time=start_time)
                # 2b) a single pickled object
                elif extension == '.pkl':
                    self._unpickle_arrivals(item,
                                            end_time=end_time,
                                            start_time=start_time)
                else:
                    message = 'rate_schedule should either contain '+\
                              'a Rate object, or a string file name that has '+\
                              'a .csv or .pkl extension.'
                    raise ValueError(message)
              
            # 3) A Record object
            elif hasattr(item,'RECORD'): 
                self._convert_record_object_to_arrivals(item,
                                                        end_time=end_time,
                                                        start_time=start_time)
            
            else:
                message = 'rate_schedule object not understood. Please, '+\
                          'provide either a rate object, record object, '+\
                          'a .csv or .pkl file name.'
                raise ValueError(message)
        
        # B) Several items and these should be Rate objects.           
        else:
            # it can only be a dictionary of rate objects.
            self._simulate_arrivals(end_time,start_time)
            
        
        if bool(self.arrival_times):
            self.current_time = self.arrival_times[-1]
        else:
            self.current_time = None
        
        return None
        
    #---------------------------------------------------------------------------
        
    def view_rate(self,data_pts=100,
                  colors=['red','blue'],
                  grid=True,
                  axes=None):
        
        '''Plots the rate intensity of the Exponential process against time
        as specified by the rate_schedule.
        
        Parameters:
        -----------
        data_pts: int
            The amount of points in the time axis. More data points leads to
            a finer plot.
        colors: list(str)
            A list of strings is to be provided. These strings must ve valid
            matplotlib colors. These colors will be cycled through and are used
            to help differentiate the piece-wise defined rate intensities.
        grid: bool
            Plots a matplotlib grid on the axes.
        axes: matplotlib.axes._subplots.AxesSubplot or None
            If set to None then a new axes will be generated along with a new
            figure. These can be accessed as class attributes.
        
        Raises:
        -------
        ValueError:
            If an invalid color is provided in the list.
        Exception:
            Once cannot view the rate intensity function of csv file or 
            pickled object. Identifying the underlying rate intensity is 
            a Signal Processing/Machine Learning problem.
        
        Returns:
        --------
        None
        '''
        
        start_time = 0
        MIN = np.inf
        MAX = -np.inf
        
        fig = None
        ax = axes

        
        for end_time in self.schedule_end_times:
            rate = self.rate_schedule[end_time]
            
            print(rate)
            
            if isinstance(rate,str):
                message = 'A file name has been given. Hence, no underlying rate '+\
                          'intensity schedule exists that can be viewed.'
                raise Exception(message)
                
            if hasattr(rate,'RECORD'):
                message = 'A Record object has been given. Hence, no underlying rate '+\
                          'intensity schedule exists that can be viewed.'
                raise Exception(message)
            
            # If code reaches this point we allow for plotting
            # Start block of code to set up plot
            if fig is None:
                if ax is None:
                    # make own axes
                    fig,ax = plt.subplots(1,1)
                else:
                    # axes was given
                    fig = True # not None hence this block of code is passed
                               # in the future.
                               
                # Save as class attributes for if we need to access it.
                self.figure = fig
                self.axes = ax
              # End block of code to set up plot. Either way fig is not None
              # and this block of code will not be passed again.
            
            T = np.linspace(start_time,end_time,data_pts)
            rates = rate(T)
            ax.plot(T,rates,color=cycle_list(colors))
            start_time = end_time
            min_ = np.min(rates)
            max_ = np.max(rates)
            if min_ < MIN:
                MIN = min_
            if max_ > MAX:
                MAX = max_
        
        for end_time in self.schedule_end_times:
            ax.vlines(end_time,MIN,MAX,linestyle='--',colors='black',alpha=0.6)
        
        ax.set_xlabel('time')
        ax.set_ylabel('rate')
        ax.set_title('Rate Schedule')
        ax.grid(grid)
        plt.show()    
        
        return None
    
    #---------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Source (ID:{0})'.format(self.ID)
        
#-------------------------------------------------------------------------------