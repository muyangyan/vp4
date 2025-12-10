import plado
from plado.parser import parse
import itertools
from typing import List, Dict, Tuple, Any

class PDDLToPRISM:
    def __init__(self, domain_file: str, problem_file: str):
        self.domain_file = domain_file
        self.problem_file = problem_file

        # Parse using plado
        self.domain, self.problem = parse(domain_file, problem_file)
        
        print("--- Domain Attributes ---")
        print(f"Domain Name: {self.domain.name}")

        # Check Requirements
        print(f"Requirements: {self.domain.requirements}")

        # Check Actions
        print(f"Action Count: {len(self.domain.actions)}")
            
        # Check Predicates
        print(f"Predicate Count: {len(self.domain.predicates)}")
        
        # Check Types
        print(f"Types: {self.domain.types[0]}")

        # Data structures to hold PRISM model components
        self.objects = self._collect_objects()
        self.ground_atoms = []
        self.ground_actions = []

    def _collect_objects(self) -> Dict[str, List[str]]:
        objs = {}
        if hasattr(self.domain, 'constants'):
            for c in self.domain.constants:
                t = getattr(c, 'type_name', 'object')
                objs.setdefault(t, []).append(c.name)

        for o in self.problem.objects:
            t = getattr(o, 'type_name', 'object')
            objs.setdefault(t, []).append(o.name)

        return objs

    def _get_objects_for_type(self, type_name: str) -> List[str]:
        if type_name == "object":
            return [o for sublist in self.objects.values() for o in sublist]
        return self.objects.get(type_name, [])
    
    def _predicate_to_prism(self, predicate: str, args: List[str]) -> str:
        return f"{predicate}_{'_'.join(args)}"

    def ground_state_variables(self):
        for predicate in self.domain.predicates:
            param_types = [ptype.type_name for ptype in predicate.parameters]
            object_lists = [self._get_objects_for_type(t) for t in param_types]

            for args in itertools.product(*object_lists):
                # Format: pred_arg1_arg2_...
                atom_name = self._predicate_to_prism(predicate.name, args)
                self.ground_atoms.append(atom_name)

        # Remove duplicates and sort
        self.ground_atoms = sorted(list(set(self.ground_atoms)))

def pddl_to_mdp(domain_file: str, problem_file: str) -> str:
    translator = PDDLToPRISM(domain_file, problem_file)

    translator.ground_state_variables()
    print("")
    print(f"Grounded Atoms: {translator.ground_atoms}")

    return ...

if __name__ == "__main__":
    mdp = pddl_to_mdp("data/deterministic/blocksworld/domain.pddl", "data/deterministic/blocksworld/1.pddl")
    print(f"Translated MDP: {mdp}")
