

import matplotlib
import warnings
import sys

# Check if __basik__ is being run from within a Jupyter Notebook or Ipython
# environment. Display components cannot be rendered in such environments as the
# kernel dies.
# If not in such an environment, check if QtA5gg Matplotlib backend is installed.
# __basik__ display components were designed around this backend.


NOTEBOOK = sys.argv[-1].endswith('json') # bool

#if not hasattr(__builtins__,'__IPYTHON__'):
if not NOTEBOOK:
    try:
        matplotlib.use('Qt5Agg')
    except ValueError:
        message = '\'Qt5Agg\' is not available as a Matplotlib backend.\n'+\
                  'As a result, refrain from using Display components in the '+\
                  'simulation. The Display components were designed to work with'+\
                  '\'Qt5Agg\' as a backend.'
        warnings.warn(message)
else:
    
    message = '__basik__ has picked up that it is currently being run from '+\
              'within a Ipython or Jupyter Notebook. Display components require'+\
              'QtA5gg to render. Most Ipython-based interactive notebooks have'+\
              'their kernel shut down when using QtA5gg as a Matplotlib backend. '+\
              'Hence, __basik__ will not use QtA5gg. As a result, please '+\
              'refrain from using __basik__ display components while in '+\
              'the Ipython or Jupyter Notebook environment. If display '+\
              'components are required, please use Ipython in a console. The '+\
              'Spyder IDE for Python is highly recommended.'
    warnings.warn(message)
    

import __main__
import matplotlib.pyplot as plt
print('Importing matplotlib.pyplot as plt\n')
setattr(__main__,'plt',plt)


from .global_queue import GlobalQueue
from .node import Node
from .RoadObject import Lane,RoadDisplay
from .VehicleObject import Vehicle,VehicleDisplay
from .CircleObject import Circle,CircleDisplay
from .TrafficLightObject import TrafficLight,TrafficLightCycle,TrafficLightDisplay
from .FlaredTrafficLightObject import FlaredTrafficLight,FlaredTrafficLightCycle,FlaredTrafficLightDisplay
from .OffRampObject import OffRamp,OffRampDisplay
from .OnRampObject import OnRamp,OnRampDisplay
from .IntersectionObject import Intersection,IntersectionDisplay
from .PedestrianCrossingObject import PedestrianCrossing,PedestrianCrossingDisplay
from .StopStreetObject import StopStreet,StopStreetDisplay
from .source import Source,MMPP_rate_schedule,Rate,reset_source_count,csv_to_source,pickle_to_source
from .record import Record
from .obstruction import Obstruction
from .simulation_session import Session
#import __basik__.FlowFunctions as FlowFunctions
from . import FlowFunctions
from .utils import axes_grid,fill_axes_grid,load_csv,load_pickle


Queue = GlobalQueue()
import __basik__.global_queue as GQ
setattr(GQ,'Queue',Queue)


reset_source_count(count=0)

__all__ = [plt,
           GlobalQueue,
           Node,
           Lane,RoadDisplay,
           Vehicle,VehicleDisplay,
           Circle,CircleDisplay,
           FlaredTrafficLight,FlaredTrafficLightCycle,FlaredTrafficLightDisplay,
           TrafficLight,TrafficLightCycle,TrafficLightDisplay,
           OffRamp,OffRampDisplay,
           OnRamp,OnRampDisplay,
           Intersection,IntersectionDisplay,
           PedestrianCrossing,PedestrianCrossingDisplay,
           StopStreet,StopStreetDisplay,
           Source,MMPP_rate_schedule,Rate,reset_source_count,csv_to_source,pickle_to_source,
           Record,
           Obstruction,
           Session,
           Queue,
           FlowFunctions,
           axes_grid,fill_axes_grid,load_csv,load_pickle]


