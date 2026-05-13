# -*- coding: utf-8 -*-
# filepath: /home/unitree/unitree_sdk2_python/example/go2/high_level/example_1.py
import sys
import time
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)
    
    # Initialize communication factory with network interface
    ChannelFactoryInitialize(0, sys.argv[1])
    
    # Create sport client object
    sport_client = SportClient()
    sport_client.SetTimeout(10.0)
    sport_client.Init()
    
    msc = MotionSwitcherClient()
    msc.SetTimeout(5.0)
    msc.Init()  # Add initialization
    msc.SelectMode("Advanced")
    # for i in range(4):
       
    #     print(f"Switching to Advanced mode in {5 - i} seconds...")
    #     sport_client.Move(0,0,0.95)
    #     time.sleep(2)
    # Execute stand up
    sport_client.Dance2()
    # time.sleep(2)
 

    

if __name__ == "__main__":
    main()