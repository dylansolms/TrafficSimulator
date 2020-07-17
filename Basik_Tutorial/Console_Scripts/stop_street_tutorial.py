'''
Runs the display of Tutorial 3.
'''


import __basik__ as bk
import numpy as np


if __name__ == '__main__':
    
    np.random.seed(123)
    print('Setting up simulation...')
    bk.VehicleDisplay.SHOW = True   # We turn on the display 
    bk.VehicleDisplay.speed_up_factor = 10  # make the display attempt to render faster
    bk.Vehicle.frames_per_move = 2 # the amount of frames per move. Larger = smoother = slower
    fig,ax = bk.axes_grid(3,3,scale=2.5)  # we build a display grid
    end_time = 20
    lane_length = 5  # SMALL: easier to see in the display.
    bk.Queue.clear()
    # North:
    Nlane_in = bk.Lane(lane_length) 
    Nlane_out = bk.Lane(lane_length) 
    NDisplay = bk.RoadDisplay(left_lane=Nlane_out,
                              right_lane=Nlane_in,
                              axes=ax[0,1],
                              horizontal=False)
    Nrate = {end_time:bk.Rate(0.8)} 
    Nsource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Nlane_in.IN,
                        rate_schedule=Nrate)
    print('Scheduling Northern arrivals...')
    Nsource.setup_arrivals(end_time)
    print('..done!')
    Nrecord = bk.Record(Nlane_out.OUT)  
    # East 
    Elane_in = bk.Lane(lane_length) 
    Elane_out = bk.Lane(lane_length)
    EDisplay = bk.RoadDisplay(left_lane=Elane_out,
                              right_lane=Elane_in,
                              axes=ax[1,2],
                              horizontal=True)
    Erate = {end_time:bk.Rate(0.8)} 
    Esource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Elane_in.IN,
                        rate_schedule=Erate)
    print('Scheduling Eastern arrivals...')
    Esource.setup_arrivals(end_time)
    print('..done!')
    Erecord = bk.Record(Elane_out.OUT)  
    # South
    Slane_in = bk.Lane(lane_length) 
    Slane_out = bk.Lane(lane_length) 
    SDisplay = bk.RoadDisplay(left_lane=Slane_in,
                              right_lane=Slane_out,
                              axes=ax[2,1],
                              horizontal=False)
    Srate = {end_time:bk.Rate(0.8)}
    Ssource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Slane_in.IN,
                        rate_schedule=Srate)
    print('Scheduling Southern arrivals...')
    Ssource.setup_arrivals(end_time)
    print('..done!')
    Srecord = bk.Record(Slane_out.OUT)  
    # West
    Wlane_in = bk.Lane(lane_length) 
    Wlane_out = bk.Lane(lane_length) 
    SDisplay = bk.RoadDisplay(left_lane=Wlane_in,
                              right_lane=Wlane_out,
                              axes=ax[1,0],
                              horizontal=True)
    Wrate = {end_time:bk.Rate(0.8)} 
    Wsource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Wlane_in.IN,
                        rate_schedule=Wrate)
    print('Scheduling Western arrivals...')
    Wsource.setup_arrivals(end_time)
    print('..done!')
    Wrecord = bk.Record(Wlane_out.OUT)  
    in_nodes = {'N':Nlane_in.OUT,'E':Elane_in.OUT,'S':Slane_in.OUT,'W':Wlane_in.OUT}
    out_nodes = {'N':Nlane_out.IN,'E':Elane_out.IN,'S':Slane_out.IN,'W':Wlane_out.IN,}
    
    transitions = {'N': {'E': 0.2, 'S': 0.6, 'W': 0.2},
                   'E': {'S': 0.2, 'W': 0.6, 'N': 0.2},
                   'S': {'W': 0.2, 'N': 0.6, 'E': 0.2},
                   'W': {'N': 0.2, 'E': 0.6, 'S': 0.2}}
    stopstreet = bk.StopStreet(in_nodes=in_nodes,
                               out_nodes=out_nodes,
                               transitions=transitions)
    stopstreetdisplay = bk.StopStreetDisplay(stop_street_object=stopstreet,
                                             show=['N','E','S','W'],
                                             axes=ax[1,1])
    
    bk.Queue.run(end_time=end_time,start_time=0)
