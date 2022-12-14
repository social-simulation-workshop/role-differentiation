from __future__ import annotations

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
        self.neighborhood = list() # list of Agent objects
        self.payoff = 0
    
    def _play_PD(self, ag_a: Agent, ag_b: Agent):
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
    
    def reset_payoff(self) -> None:
        self.payoff = 0
    
    def interacting(self) -> None:
        for neighbor in self.neighborhood:
            self._play_PD(self, neighbor)
    
    def _find_neighbor_idx(self, ag_id: int) -> int:
        return [nei.id for nei in self.neighborhood].index(ag_id)
        
    def remove_neighbor(self, ag_id: int) -> None:
        self.neighborhood.pop(self._find_neighbor_idx(ag_id))
    
    def update_strategy_neighborhood(self, network: Network) -> bool:
        """
        Return True if the strategy is updated, False if not.
        """
        updated = False
        all_ag_payoff = [neighbor.payoff for neighbor in self.neighborhood] + [self.payoff]
        if np.max(all_ag_payoff) > self.payoff: # unsatisfied
            leader_ag = self.neighborhood[np.random.choice(np.argwhere(all_ag_payoff == np.max(all_ag_payoff)).flatten())]
            # update strategy 
            if self.strategy != leader_ag.strategy:
                updated = True
                network.coop_num += leader_ag.strategy - self.strategy
                self.strategy = leader_ag.strategy
            # update neighborhood
            if self.strategy == Agent.DEFECT and draw(self.args.p):
                updated = True
                self._update_neighborhood(network, leader_ag)
        return updated
    
    def _update_neighborhood(self, network: Network, leader_ag: Agent) -> None:
        def get_new_tie() -> int:
            a = np.random.choice(self.args.N)
            while a == self.id or Network.encode_tie(a, self.id) in network.ties:
                a = np.random.choice(self.args.N)
            return a

        # remove old tie
        # handle the case where two defector are the leader in each other's neighborhood
        if Network.encode_tie(self.id, leader_ag.id) in network.ties:
            self.remove_neighbor(leader_ag.id)
            leader_ag.remove_neighbor(self.id)
            network.ties.remove(Network.encode_tie(self.id, leader_ag.id))
        
        # build new tie
        ag_b_id = get_new_tie()
        ag_b = network.ags[ag_b_id]
        self.neighborhood.append(network.ags[ag_b_id])
        ag_b.neighborhood.append(self)
        network.ties.add(Network.encode_tie(self.id, ag_b_id))
    
    def get_string_strategy(self) -> str:
        return "C" if self.strategy == Agent.COOPERATE else "D"
    
    def get_neighbor_id(self) -> list:
        return [nei.id for nei in self.neighborhood]


class Network:
    RUNNING = 0
    STATIONARY_STATE = 1
    ALL_D_STATE = 2
    
    def __init__(self, args: argparse.ArgumentParser, random_seed):
        Agent._ids = itertools.count(0)
        np.random.seed(random_seed)
        self.args = args
        print(args)

        # network states
        self.coop_num = None 

        self.ags = self.init_agents()
        self.ties = self.init_network() # a set of encoded strings consisting of two agents' id

        self.final_state = Network.RUNNING 
        self.fc_his = list()
    
    def init_agents(self) -> list:
        print("Initializing {} agents ...".format(self.args.N))
        self.coop_num = int(self.args.N * self.args.coop_init_fraction)
        init_strategy_distribution = [Agent.COOPERATE]*self.coop_num + [Agent.DEFECT]*(self.args.N - self.coop_num)
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
    
    def simulate(self) -> bool:
        """ Return True if the model reaches the stationary state, False if not. """
        # print("init | fc {}".format(self.get_fc()))
        # for ag_idx, ag in enumerate(self.ags):
        #     print("ag {} ({}) | neighbor: {}".format(
        #         ag_idx, ag.get_string_strategy(), ag.get_neighbor_id()))
        
        for iter_idx in range(self.args.n_iter):
            updated = False

            for ag in self.ags:
                ag.reset_payoff()

            for ag in self.ags:
                ag.interacting()
            
            for ag in self.ags:
                updated = ag.update_strategy_neighborhood(self) or updated

            print("b, p = ({:.2f}, {:.2f}) | iter {} | fc {}".format(self.args.T, self.args.p, iter_idx, self.get_fc()))
            
            self.fc_his.append(self.get_fc())

            assert len(self.ties) == int(self.args.K * self.args.N / 2)

            if not updated: # reach stationary point
                self.final_state = Network.STATIONARY_STATE
                break 

            if self.fc_his[-1] == 0.0: # reach all-D trap
                self.final_state = Network.STATIONARY_STATE if self.args.p == 0.0 else Network.ALL_D_STATE
                break
                
        return True if self.final_state == Network.STATIONARY_STATE else False

    def get_fc(self):
        return self.coop_num / self.args.N
    
    def get_final_fc(self) -> float:
        if self.final_state == Network.RUNNING:
            return np.mean(self.fc_his[-100:])
        else:
            return self.fc_his[-1]
    
    def reach_stationary_state(self) -> bool:
        return True if self.final_state == Network.STATIONARY_STATE else False
    
    def reach_all_d_state(self) -> bool:
        return True if self.final_state == Network.ALL_D_STATE else False
        
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
            