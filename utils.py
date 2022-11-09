import argparse
import itertools
import numpy as np


def draw(p) -> bool:
    return True if np.random.uniform() < p else False

class Agent:
    _ids = itertools.count(0)

    COOPERATE = 1
    DEFECT = 0
    R = 1
    P = 0
    S = 0

    def __init__(self, strategy, args: argparse.ArgumentParser):
        self.id = next(self._ids)
        self.args = args

        self.strategy = strategy
        self.neighborhood = list()
        self.payoff = 0
    
    def _play_PD(self, ag_a, ag_b):
        if ag_a.strategy == Agent.COOPERATE and ag_b.strategy == Agent.COOPERATE:
            ag_a.payoff += Agent.R
            ag_b.payoff += Agent.R
        if ag_a.strategy == Agent.DEFECT and ag_b.strategy == Agent.COOPERATE:
            ag_a.payoff += self.args.T
            ag_b.payoff += Agent.S
        if ag_a.strategy == Agent.COOPERATE and ag_b.strategy == Agent.DEFECT:
            ag_a.payoff += Agent.S
            ag_b.payoff += self.args.T
        if ag_a.strategy == Agent.DEFECT and ag_b.strategy == Agent.DEFECT:
            ag_a.payoff += Agent.P
            ag_b.payoff += Agent.P
    
    def interacting(self) -> None:
        self.payoff = 0
        for neighbor in self.neighborhood:
            self._play_PD(self, neighbor)
    
    def find_neighbor(self, ag_id: int) -> int:
        return [nei.id for nei in self.neighborhood].index(ag_id)
        
    def remove_neighbor(self, ag_id: int) -> None:
        self.neighborhood.pop(self.find_neighbor(ag_id))
    
    def _get_leader_id(self) -> int:
        all_ag_payoff = [neighbor.payoff for neighbor in self.neighborhood] + [self.payoff]
        leader_idx = np.random.choice(np.argwhere(all_ag_payoff == np.max(all_ag_payoff)).flatten())
        return self.neighborhood[leader_idx].id if leader_idx != len(self.neighborhood) else self.id

    def update_strategy(self, network) -> bool:
        """
        Return True if the strategy is updated, False if not.
        """
        leader_id = self._get_leader_id()
        leader_ag = self.neighborhood[leader_id]

        updated = False
        if self.leader_id != self.id:
            # imitate the neighbor the largest payoff
            if self.strategy != leader_ag.strategy:
                updated = updated or True
                network.coop_num += leader_ag.strategy - self.strategy
                self.strategy = leader_ag.strategy
            # update neighbor
            if self.strategy == Agent.DEFECT and draw(self.args.p):
                updated = updated or True
                self._update_neighborhood(network, leader_ag)
        return updated
    
    def _update_neighborhood(self, network, leader_ag) -> None:
        def get_new_tie() -> int:
            a = np.random.choice(self.args.N)
            while a == self.id or Network.encode_tie(a, self.id) in network.ties:
                a = np.random.choice(self.args.N)
            return a

        # remove old tie
        if Network.encode_tie(self.id, leader_ag.id) in network.ties:
            self.remove_neighbor(leader_ag.id)
            leader_ag.remove_neighbor(self.id)
            network.ties.remove(Network.encode_tie(self.id, leader_ag.id))

        # # handle the case where two defector are the leader in each other's neighborhood
        # if leader_ag.leader_id == self.id:
        #     leader_ag.leader_id = None
        # # print("remove tie {} <-> {}".format(self.id, leader_ag.id))
        
        # build new tie
        ag_b_id = get_new_tie()
        self.neighborhood.append(network.ags[ag_b_id])
        network.ags[ag_b_id].neighborhood.append(self)
        network.ties.add(Network.encode_tie(self.id, ag_b_id))
        # print("add tie {} <-> {}".format(self.id, ag_b_id))
    
    def get_string_strategy(self) -> str:
        return "C" if self.strategy == Agent.COOPERATE else "D"
    
    def get_neighbor_id(self) -> list:
        return [nei.id for nei in self.neighborhood]


class Network:
    
    def __init__(self, args: argparse.ArgumentParser, random_seed):
        Agent._ids = itertools.count(0)
        np.random.seed(random_seed)
        self.args = args
        print(args)

        # network states
        self.coop_num = None 

        self.ags = self.init_agents()
        self.ties = self.init_network()
    
    def init_agents(self) -> list:
        print("Initializing {} agents ...".format(self.args.N))
        self.coop_num = int(self.args.N * self.args.coop_init_fraction)
        init_strategy_distribution = [1]*self.coop_num + [0]*(self.args.N - self.coop_num)
        np.random.shuffle(init_strategy_distribution)
        return [Agent(strat, self.args) for strat in init_strategy_distribution]
    
    @staticmethod
    def encode_tie(ag_a_id: int, ag_b_id: int) -> str:
        if ag_a_id == ag_b_id:
            raise Exception("invalid tie")
        if ag_a_id > ag_b_id:
            ag_a_id, ag_b_id = ag_b_id, ag_a_id
        return "{} <-> {}".format(ag_a_id, ag_b_id)
    
    def init_network(self) -> set:
        def get_new_tie(ties: set):
            a, b = np.random.choice(self.args.N, size=2, replace=False)
            while Network.encode_tie(a, b) in ties:
                a, b = np.random.choice(self.args.N, size=2, replace=False)
            return a, b
        
        print("Initializing {} ties ...".format(int(self.args.K * self.args.N / 2)))
        ties = set()
        for _ in range(int(self.args.K * self.args.N / 2)):
            ag_a_id, ag_b_id = get_new_tie(ties)
            self.ags[ag_a_id].neighborhood.append(self.ags[ag_b_id])
            self.ags[ag_b_id].neighborhood.append(self.ags[ag_a_id])
            ties.add(self.encode_tie(ag_a_id, ag_b_id))
        return ties
    
    def simulate(self) -> float:
        # print("init | fc {}".format(self.get_fc()))
        # for ag_idx, ag in enumerate(self.ags):
        #     print("ag {} ({}) | neighbor: {}".format(
        #         ag_idx, ag.get_string_strategy(), ag.get_neighbor_id()))
        
        for iter_idx in range(self.args.n_iter):
            updated = False

            for ag in self.ags:
                ag.interacting()

            print("b, p = ({:.2f}, {:.2f}) | iter {} | fc {}".format(self.args.T, self.args.p, iter_idx, self.get_fc()))
            # for ag_idx, ag in enumerate(self.ags):
            #     leader_idx = ag._get_leader_idx()
            #     leader_id = ag.neighborhood[leader_idx].id if leader_idx != len(ag.neighborhood) else ag.id
            #     print("ag {} ({}) | payoff {:.1f} | leader {} | neighbor: {}".format(
                    # ag_idx, ag.get_string_strategy(), ag.payoff, leader_id, ag.get_neighbor_id()))
            
            for ag in self.ags:
                updated = ag.update_strategy(self) or updated
            
            for ag in self.ags:
                updated = ag.update_neighborhood(self) or updated
            
            assert len(self.ties) == int(self.args.K * self.args.N / 2)

            if not updated: # reach stationary point
                break

            if self.get_fc() == 0.0: # reach all-D trap
                break
    
    def get_fc(self) -> float:
       return self.coop_num / self.args.N
        
    def get_avg_payoff_C_D(self):
        c_payoff_sum, d_payoff_sum = 0, 0
        for ag in self.ags:
            if ag.strategy == Agent.COOPERATE:
                c_payoff_sum += ag.payoff
            elif ag.strategy == Agent.DEFECT:
                d_payoff_sum += ag.payoff
        return c_payoff_sum / self.coop_num, d_payoff_sum / (self.args.N - self.coop_num)
    
    def get_avg_payoff_diff(self):
        c_avg_payoff, d_avg_payoff = self.get_avg_payoff_C_D()
        return d_avg_payoff - c_avg_payoff
            