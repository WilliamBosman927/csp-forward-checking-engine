"""
CSP Forward Checking and Domain Pruning Engine
Author: Open-Source Constraint Logic Community
Description: Proactively filters future timeline domains using deepcopy to prevent dead-ends.
"""
import copy

class TemporalCSPPropagator:
    def __init__(self, travel_matrix, durations):
        self.travel_matrix = travel_matrix
        self.durations = durations

    def apply_forward_checking(self, current_place, assigned_time, unassigned_places, current_domains):
        """
        Executes proactive domain pruning via Forward Checking.
        Returns: (is_valid_branch: bool, new_pruned_domains: dict)
        """
        # Deepcopy prevents leaking back-tracking adjustments to parent frames
        new_domains = copy.deepcopy(current_domains)
        is_valid_branch = True
        
        for next_place in unassigned_places:
            if next_place == current_place:
                continue
                
            valid_times = []
            for next_t in new_domains[next_place]:
                transit_to = self.travel_matrix.get((current_place, next_place), float('inf'))
                transit_from = self.travel_matrix.get((next_place, current_place), float('inf'))
                
                # Temporal mutual exclusion check
                if (assigned_time + self.durations[current_place] + transit_to <= next_t) or \
                   (next_t + self.durations[next_place] + transit_from <= assigned_time):
                    valid_times.append(next_t)
                    
            new_domains[next_place] = valid_times
            
            # Domain Wipe-out triggers immediate pruning
            if len(new_domains[next_place]) == 0:
                is_valid_branch = False
                break
                
        return is_valid_branch, new_domains

# --- Mock Test ---
if __name__ == "__main__":
    matrix = {("SpotA", "SpotB"): 30, ("SpotB", "SpotA"): 30}
    durations = {"SpotA": 120, "SpotB": 60}
    domains = {"SpotA": [540, 600], "SpotB": [600, 660, 720]}
    
    propagator = TemporalCSPPropagator(matrix, durations)
    valid, new_dom = propagator.apply_forward_checking("SpotA", 540, ["SpotB"], domains)
    print(f"Branch Valid: {valid}, Pruned Domains for SpotB: {new_dom['SpotB']}")