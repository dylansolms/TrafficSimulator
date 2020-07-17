'''
Produces the type 1 obstruction crossing from Tutorial 7.
'''

import numpy as np
import __basik__ as bk


if __name__ == '__main__':
    
    end_time = 20
    np.random.seed(123)
    fig,ax = plt.subplots(1,1)
    # Let us create a single lane object
    lane = bk.Lane(10)
    lane_display = bk.RoadDisplay(left_lane=lane,
                                  right_lane=None,
                                  axes=ax,
                                  horizontal=True)
    rate = {end_time:bk.Rate(0.3)} 
    source = bk.Source(vehicle_velocity = 16.67,  
                       target_node = lane.IN,
                       rate_schedule=rate)
    source.setup_arrivals(20)
    # Let us schedule three obstructions at some node
    lane.nodes[4].schedule_obstructions(start_times=[0,20], 
                                        durations=[9,5])
    # Run

    bk.Queue.run(end_time)