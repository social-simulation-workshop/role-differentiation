import numpy as np
import os
import sys

from args import ArgsConfig
from utils import Network, Agent 


if __name__ == "__main__":
   parser = ArgsConfig()
   args = parser.get_args()

   net = Network(args, args.random_seed)
   net.simulate()
   print(net.get_fc())