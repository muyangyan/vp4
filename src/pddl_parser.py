import plado
from plado.parser import parse
import itertools
from typing import List, Dict, Tuple, Any, Optional

class PDDLToPRISM:
    def __init__(self, domain_file: str, problem_file: str):
        self.domain_file = domain_file
        self.problem_file = problem_file
        self.domain, self.problem = parse(domain_file, problem_file)
        
        # Data structures
        self.objects = self._collect_objects()
        self.ground_atoms = []
        self.ground_actions = []

    def _collect_objects(self) -> Dict[str, List[str]]:
        objs = {}
        if hasattr(self.domain, 'constants') and self.domain.constants:
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
        clean_args = [a.replace('-', '_') for a in args]
        clean_pred = predicate.replace('-', '_')
        return f"{clean_pred}_{'_'.join(clean_args)}"

    # --- DUCK TYPING HELPERS ---
    
    def _get_list_content(self, obj: Any) -> Optional[List[Any]]:
        """
        Returns the list content if the object acts like a container.
        Checks standard PDDL/PPDDL attributes.
        """
        # PPDDL: outcomes
        # PDDL: effects, sub_formulas, parts, children
        for attr in ['outcomes', 'effects', 'sub_formulas', 'parts', 'children', 'operands', 'effect_list']:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                if isinstance(val, (list, tuple)): 
                    return val
        return None

    def _get_child_content(self, obj: Any) -> Any:
        """
        Returns the single child if the object acts like a wrapper (e.g. NOT).
        """
        # Plado 'NegativeEffect' uses .atom
        # Standard Logic 'Not' uses .expression or .operand
        for attr in ['atom', 'expression', 'operand', 'effect', 'argument']:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                if val is not None: return val
        return None

    def _get_atom_details(self, obj: Any) -> Optional[Tuple[str, List[Any]]]:
        """
        Extracts (name, args) if the object acts like an Atom.
        """
        pred_name = None
        args = []
        
        # Case 1: Direct Atom
        if hasattr(obj, 'name') and hasattr(obj, 'arguments'):
            pred_name = obj.name
            args = obj.arguments
        # Case 2: Wrapper (e.g. Predicate reference)
        elif hasattr(obj, 'predicate'):
            pred_name = obj.predicate.name
            args = getattr(obj, 'arguments', [])
            
        if pred_name:
            return pred_name, args
        return None

    # --- TRANSLATION LOGIC ---

    def ground_state_variables(self):
        for predicate in self.domain.predicates:
            param_types = [ptype.type_name for ptype in predicate.parameters]
            object_lists = [self._get_objects_for_type(t) for t in param_types]
            for args in itertools.product(*object_lists):
                atom_name = self._predicate_to_prism(predicate.name, args)
                self.ground_atoms.append(atom_name)
        self.ground_atoms = sorted(list(set(self.ground_atoms)))

    def _translate_expression(self, expr: Any, var_map: Dict[str, str]) -> str:
        if not expr: return "true"
        typename = type(expr).__name__.lower()

        # 1. Container (AND / OR)
        # We rely on the attribute check, then fallback to typename for logic operator
        children = self._get_list_content(expr)
        if children is not None:
            parts = [self._translate_expression(e, var_map) for e in children]
            if 'or' in typename or 'disjunct' in typename:
                return f"({' | '.join(parts)})" if parts else "false"
            # Default to AND
            return f"({' & '.join(parts)})" if parts else "true"

        # 2. Negation (NOT)
        if 'not' in typename or 'neg' in typename:
            child = self._get_child_content(expr)
            if child: return f"!({self._translate_expression(child, var_map)})"
            return "true"

        # 3. Atom
        atom_data = self._get_atom_details(expr)
        if atom_data:
            pred_name, args = atom_data
            ground_args = [var_map.get(arg.name, arg.name) for arg in args]
            return self._predicate_to_prism(pred_name, ground_args)

        return "true"

    def _effect_to_assignments(self, effect: Any, var_map: Dict[str, str]) -> List[Tuple[str, bool]]:
        """
        Recursively extracts deterministic updates: [(var_name, True/False)]
        """
        if not effect: return []
        typename = type(effect).__name__.lower()

        # 1. Container (List of effects)
        children = self._get_list_content(effect)
        if children is not None:
            assignments = []
            for e in children:
                assignments.extend(self._effect_to_assignments(e, var_map))
            return assignments

        # 2. Negation (Delete list)
        if 'not' in typename or 'neg' in typename:
            child = self._get_child_content(effect)
            if child:
                pos_assigns = self._effect_to_assignments(child, var_map)
                return [(atom, False) for atom, val in pos_assigns]
            return []

        # 3. Atom (Add list)
        atom_data = self._get_atom_details(effect)
        if atom_data:
            pred_name, args = atom_data
            ground_args = [var_map.get(arg.name, arg.name) for arg in args]
            atom = self._predicate_to_prism(pred_name, ground_args)
            return [(atom, True)]

        return []

    def _process_effects(self, effects: Any, var_map: Dict[str, str]) -> Optional[List[Tuple[float, str]]]:
        if not effects: return [(1.0, "true")]
        
        # --- PROBABILISTIC CHECK ---
        # Duck Typing: If it has 'outcomes', it's a PPDDL Probabilistic Effect
        outcomes_list = []
        
        if hasattr(effects, 'outcomes'):
             # This is a Probabilistic Effect
             for outcome in effects.outcomes:
                # Extract Probability
                p_val = 1.0
                if hasattr(outcome, 'probability'):
                    p = outcome.probability
                    p_val = float(p.value) if hasattr(p, 'value') else float(p)
                
                # Extract Effect
                eff = getattr(outcome, 'effect', None)
                assigns = self._effect_to_assignments(eff, var_map)
                outcomes_list.append((p_val, assigns))
        else:
            # Deterministic Effect
            assigns = self._effect_to_assignments(effects, var_map)
            outcomes_list.append((1.0, assigns))

        # --- CONFLICT RESOLUTION & FORMATTING ---
        final_results = []
        for prob, assigns in outcomes_list:
            state_map = {}
            possible = True
            
            for atom, val in assigns:
                # Check for contradiction (True AND False)
                if atom in state_map and state_map[atom] != val:
                    possible = False 
                    break
                state_map[atom] = val
            
            if not possible:
                # Impossible action branch -> Drop action entirely
                return None 
            
            if not state_map:
                update_str = "true"
            else:
                parts = [f"({atom}' = {'true' if val else 'false'})" for atom, val in state_map.items()]
                update_str = " & ".join(parts)
            
            final_results.append((prob, update_str))

        return final_results

    def ground_actions_logic(self):
        for action in self.domain.actions:
            param_names = [ptype.name for ptype in action.parameters]
            param_types = [ptype.type_name for ptype in action.parameters]
            object_lists = [self._get_objects_for_type(t) for t in param_types]

            for args in itertools.product(*object_lists):
                var_map = dict(zip(param_names, args))
                action_name = self._predicate_to_prism(action.name, list(args))
                
                guard = self._translate_expression(action.precondition, var_map)
                
                # Returns None if action contains contradictions
                updates_list = self._process_effects(action.effect, var_map)

                if updates_list is not None:
                    self.ground_actions.append({
                        "name": action_name,
                        "guard": guard,
                        "updates": updates_list
                    })

    def _write_initial_state(self, lines: List[str]) -> None:
        lines = []
        init_facts = set()
        for atom in self.problem.initial:
            args = [arg.name for arg in atom.arguments]
            init_facts.add(self._predicate_to_prism(atom.name, args))

        for atom in self.ground_atoms:
            val = "true" if atom in init_facts else "false"
            lines.append(f"\t{atom} : bool init {val};")
        return lines

    def generate_mdp(self) -> str:
        lines = ["mdp", "", "module main"]
        
        lines.extend(self._write_initial_state(lines))

        lines.append("")

        for action in self.ground_actions:
            updates_strs = []
            for prob, update in action['updates']:
                updates_strs.append(f"{prob} : {update}")
            full_update = " + ".join(updates_strs)
            lines.append(f"\t[{action['name']}] {action['guard']} -> {full_update};")

        lines.append("endmodule")
        return "\n".join(lines)
    
    def generate_dtmc(self, policy: dict) -> str:
        lines = ["dtmc", "", "module main"]

        lines.extend(self._write_initial_state(lines))

        # write rules from policy
        for rule in policy:
            # ground 
            lifted_action = rule['then']
            for 


            lines.append(f"\t[{rule['name']}] {rule['if']} -> {rule['updates']};")

        lines.append("endmodule")
        return "\n".join(lines)

def pddl_to_mdp(domain_file: str, problem_file: str) -> str:
    translator = PDDLToPRISM(domain_file, problem_file)
    translator.ground_state_variables()
    translator.ground_actions_logic()
    return translator.generate_mdp()

if __name__ == "__main__":
    mdp_str = pddl_to_mdp("data/deterministic/blocksworld/domain.pddl", "data/deterministic/blocksworld/1.pddl")
    # mdp_str = pddl_to_mdp("data/stochastic/bomb-in-toilet/domain.pddl", "data/stochastic/bomb-in-toilet/1.pddl")
    print("----- Generated MDP -----")
    print(mdp_str)
    print("-------------------------")
    with open("tmp/generated_mdp.prism", "w") as f:
        f.write(mdp_str)