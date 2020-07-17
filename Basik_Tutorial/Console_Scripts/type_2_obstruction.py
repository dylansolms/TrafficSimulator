'''
Produces the type 2 obstruction crossing from Tutorial 7.
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
    rate = {end_time:bk.Rate(0.9)} 
    source = bk.Source(vehicle_velocity = 16.67,  
                       target_node = lane.IN,
                       rate_schedule=rate)
    source.setup_arrivals(20)
    # Let us schedule three obstructions at some node
    lane.nodes[8].schedule_n_obstructions(n=4,  # how many vehicles to obstruct/delay
                                          duration=1) # duration of the delay
    # Run

    bk.Queue.run(end_time)