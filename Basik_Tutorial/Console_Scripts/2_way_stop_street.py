'''
Produces two-way stop street display from Tutorial 3.
'''

import numpy as np
import __basik__ as bk

if __name__ == '__main__':
    
    print('Setting up simulation...')
    np.random.seed(123)
    fig,ax = bk.axes_grid(3,1,scale=2.5)  
    end_time = 20
    lane_length = 5  
    bk.Queue.clear()
    # North:
    Nlane_in = bk.Lane(lane_length) 
    Nlane_out = bk.Lane(lane_length) 
    NDisplay = bk.RoadDisplay(left_lane=Nlane_out,
                              right_lane=Nlane_in,
                              axes=ax[0,0],
                              horizontal=False)
    Nrate = {end_time:bk.Rate(2)} 
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
    Srate = {end_time:bk.Rate(2)}
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

    transitions = {'N': {'E': 0, 'S': 1, 'W': 0},
               'E': {'S': 0.2, 'W': 0.6, 'N': 0.2},
               'S': {'W': 0, 'N': 1, 'E': 0},
               'W': {'N': 0.2, 'E': 0.6, 'S': 0.2}}

    stopstreet = bk.StopStreet(in_nodes=in_nodes,
                               out_nodes=out_nodes,
                               transitions=transitions)
    stopstreetdisplay = bk.StopStreetDisplay(stop_street_object=stopstreet,
                                             show=['N','S'],
                                             axes=ax[1,0])
    
    bk.Queue.run(end_time)