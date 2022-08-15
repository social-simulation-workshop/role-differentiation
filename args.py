import argparse

class ArgsConfig:
    
    def __init__(self) -> None:
        super().__init__()
    
        parser = argparse.ArgumentParser()

        parser.add_argument("--N", type=int, default=10000,
            help="")
        parser.add_argument("--K", type=int, default=8,
            help="")
        parser.add_argument("--T", type=float, default=1.2,
            help="")
        parser.add_argument("--p", type=float, default=0.0,
            help="")
        parser.add_argument("--coop_init_fraction", type=float, default=0.6,
            help="")
        parser.add_argument("--n_iter", type=int, default=1000,
            help="")
        parser.add_argument("--n_replication", type=int, default=100,
            help="")
        parser.add_argument("--random_seed", type=int, default=1025, 
            help="")

        self.parser = parser

    def get_args(self):
        args = self.parser.parse_args()
        return args
