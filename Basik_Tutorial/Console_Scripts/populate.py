'''
Produces the experiment from Tutorial 3 where the simulator is populated without
display and then run with display.
'''


import numpy as np
import __basik__ as bk

if __name__ == '__main__':

    #--------------------------------------------------------------------------
    
    # WITHOUT DISPLAY
    
    bk.VehicleDisplay.SHOW = False # TURN OFF
    print('DISPLAY OFF')
    print('Setting up simulation...')
    np.random.seed(123)
    fig,ax = bk.axes_grid(3,1,scale=2.5)  
    end_time = 5
    lane_length = 5 
    bk.Queue.clear()
    # North:
    Nlane_in = bk.Lane(lane_length) 
    Nlane_out = bk.Lane(lane_length) 
    NDisplay = bk.RoadDisplay(left_lane=Nlane_out,
                              right_lane=Nlane_in,
                              axes=ax[0,0],
                              horizontal=False)
    Nrate = {end_time:bk.Rate(1.3)} 
    Nsource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Nlane_in.IN,
                        rate_schedule=Nrate)
    print('Scheduling Northern arrivals...')
    Nsource.setup_arrivals(end_time)
    print('..done!')
    Nrecord = bk.Record(Nlane_out.OUT)
    # South
    Slane_in = bk.Lane(lane_length) 
    Slane_out = bk.Lane(lane_length) 
    SDisplay = bk.RoadDisplay(left_lane=Slane_in,
                              right_lane=Slane_out,
                              axes=ax[2,0],
                              horizontal=False)
    Srate = {end_time:bk.Rate(1.5)}
    Ssource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Slane_in.IN,
                        rate_schedule=Srate)
    print('Scheduling Southern arrivals...')
    Ssource.setup_arrivals(end_time)
    print('..done!')
    Srecord = bk.Record(Slane_out.OUT) 
    # Stops street
    in_nodes = {'N':Nlane_in.OUT,'E':None,'S':Slane_in.OUT,'W':None}
    out_nodes = {'N':Nlane_out.IN,'E':None,'S':Slane_out.IN,'W':None}
    transitions = {'N': {'E': 0, 'S': 1, 'W': 0}, # IMPORTANT
                   'E': {'S': 1, 'W': 0, 'N': 0}, # FICTITIOUS
                   'S': {'W': 0, 'N': 1, 'E': 0}, # IMPORTANT
                   'W': {'N': 1, 'E': 0, 'S': 0}} # FICTITIOUS
    stopstreet = bk.StopStreet(in_nodes=in_nodes,
                               out_nodes=out_nodes,
                               transitions=transitions)
    stopstreetdisplay = bk.StopStreetDisplay(stop_street_object=stopstreet,
                                             show=['N','S'],
                                             axes=ax[1,0])
    print('Populating simulation until: {0} seconds...'.format(end_time/2))
    bk.Queue.run(end_time/2)
    print('...done!')
    
    #--------------------------------------------------------------------------
    
    # WITH DISPLAY
    print('Turning on display...')
    bk.VehicleDisplay.SHOW = True # TURN OFF
    for component in bk.Queue.content:
        if isinstance(component,bk.Vehicle):  
            display = component.vehicle_display      
            display.show()
    print('...done!')

    start_time = bk.Queue.current_time
    print('Performing simulation with display...')
    bk.Queue.run(end_time=end_time,
                 start_time=start_time)
    print('...done!')
    
    
    #--------------------------------------------------------------------------