import re
import tempfile
import os
import itertools
from typing import List, Dict, Tuple, Any, Optional
import re

# --- PLADO IMPORT & MONKEY PATCH ---
# We patch the Plado parser to bypass its sanity checks, which are buggy
# and crash on valid PDDL actions that have no preconditions.
import plado.parser

def _dummy_make_checks(domain, problem, file=None):
    # Returning False signals "No errors found", allowing parsing to proceed.
    return False

if hasattr(plado.parser, 'sanity_checks'):
    plado.parser.sanity_checks.make_checks = _dummy_make_checks
plado.parser.make_checks = _dummy_make_checks

from plado.parser import parse


class PPDDLToPRISM:
    def __init__(self, domain_file: str, problem_file: str):
        # 1. Preprocess the input files to fix syntax issues (e.g. (:requirements) in problem file)
        #    and handle probabilistic initialization (Probabilistic Setup pattern).
        print(f"--- PREPROCESSING: {problem_file} ---")
        self.clean_domain, self.clean_problem = self._preprocess(domain_file, problem_file)

        # 2. Parse using Plado (with sanity checks disabled via monkey patch).
        try:
            self.domain_file = self.clean_domain
            self.problem_file = self.clean_problem
            self.domain, self.problem = parse(self.clean_domain, self.clean_problem)
        finally:
            # We keep the temp files for reference; in production, you might delete them here.
            pass

        # 3. Initialize data structures for the MDP translation.
        self.objects = self._collect_objects()
        self.ground_atoms = []
        self.ground_actions = []

        # define helper maps
        self.name_to_pred_map = {n:p for n, p in zip([p.name for p in self.domain.predicates], self.domain.predicates)}

    # --- INLINE PREPROCESSOR ---
    def _preprocess(self, d_path, p_path):
        """
        Reads raw PDDL files and fixes common issues that break strict parsers:
        1. Removes (:requirements) from the problem file.
        2. Converts (probabilistic ...) initial states into a deterministic setup action.
        """
        with open(d_path, 'r') as f: d_text = f.read()
        with open(p_path, 'r') as f: p_text = f.read()

        # Fix 1: Remove (:requirements) block from problem file.
        p_text = re.sub(r'\(:requirements[^)]+\)', '', p_text)

        # Fix 2: Handle Probabilistic Init.
        # Detects if (:init (probabilistic ...)) is used and transforms it into
        # a 'prob_setup_init' action in the domain, starting the problem in a 'not-setup' state.
        init_data = self._extract_balanced_block(p_text, '(:init')
        if init_data and 'probabilistic' in init_data[2]:
            print("  [Preprocessor] Converting Probabilistic Init to 'Probabilistic Setup' action...")
            start, end, init_block = init_data
            prob_data = self._extract_balanced_block(init_block, 'probabilistic')
            
            if prob_data:
                # Extract the probability specifications (e.g., "0.5 (A) 0.5 (B)")
                inner_prob = prob_data[2].replace('(probabilistic', '', 1).strip()[:-1]
                
                # Replace problem init with a deterministic flag state.
                new_init = "(:init (not-setup))"
                p_text = p_text[:start] + new_init + p_text[end:]
                
                # Add the 'not-setup' predicate to the domain.
                if '(:predicates' in d_text:
                    d_text = d_text.replace('(:predicates', '(:predicates (not-setup)')
                
                # Inject the 'prob_setup_init' action into the domain.
                setup_action = f"\n(:action prob_setup_init :parameters () :precondition (not-setup) :effect (and (not (not-setup)) (probabilistic {inner_prob})))\n"
                
                d_text = d_text.strip()
                last_paren = d_text.rfind(')')
                if last_paren != -1:
                    d_text = d_text[:last_paren] + setup_action + ")"
                else:
                    d_text += setup_action

        # Helper to write content to temporary files.
        def write_tmp(content, suffix):
            tf = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
            tf.write(content)
            tf.close()
            return tf.name
            
        return write_tmp(d_text, "domain_fixed.pddl"), write_tmp(p_text, "problem_fixed.pddl")

    def _extract_balanced_block(self, text, start_keyword):
        """Helper to extract a full parenthesized block by counting balance."""
        start_idx = text.find(start_keyword)
        if start_idx == -1: return None
        open_paren = text.rfind('(', 0, start_idx + len(start_keyword))
        if open_paren == -1: return None
        balance = 0
        for i in range(open_paren, len(text)):
            if text[i] == '(': balance += 1
            elif text[i] == ')': balance -= 1
            if balance == 0: return (open_paren, i + 1, text[open_paren:i+1])
        return None

    # --- DATA COLLECTION HELPERS ---
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
        """Converts PDDL predicate format (name, [arg1, arg2]) to PRISM variable name (name_arg1_arg2)."""
        clean_pred = predicate.replace('-', '_')
        if not args: return clean_pred
        clean_args = [a.replace('-', '_') for a in args]
        return f"{clean_pred}_{'_'.join(clean_args)}"

    # --- DUCK TYPING & ATTRIBUTE SCANNING ---
    def _get_list_content(self, obj: Any) -> Optional[List[Any]]:
        """Finds list-like content (e.g. for AND/OR blocks) by checking common attributes."""
        for attr in ['outcomes', 'effects', 'sub_formulas', 'parts', 'children', 'operands', 'effect_list']:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                if isinstance(val, (list, tuple)): return val
        return None

    def _get_child_content(self, obj: Any) -> Any:
        """
        Finds the single child object (e.g. for NOT wrappers).
        Uses a deep scan to robustly find content even if attributes are non-standard.
        """
        # 1. Check known standard attributes first.
        candidates = ['atom', 'expression', 'operand', 'effect', 'argument', 'op', 'condition', 'formula', 'prop']
        for attr in candidates:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                if val is not None: return val
        
        # 2. Fallback: Deep scan of the object's directory.
        for attr in dir(obj):
            if attr.startswith('_'): continue
            val = getattr(obj, attr)
            if hasattr(val, 'name') or hasattr(val, 'predicate') or hasattr(val, 'op') or hasattr(val, 'sub_formulas'):
                return val
        return None

    def _get_atom_details(self, obj: Any) -> Optional[Tuple[str, List[Any]]]:
        """Extracts (name, arguments) from an atomic formula object."""
        if hasattr(obj, 'name') and hasattr(obj, 'arguments'): return obj.name, obj.arguments
        elif hasattr(obj, 'predicate'): return obj.predicate.name, getattr(obj, 'arguments', [])
        return None

    # --- PROBABILITY EXTRACTION ---
    def _resolve_prob(self, prob_obj: Any) -> float:
        """
        Extracts a float probability from Plado objects.
        Handles floats, strings, NumericConstant wrappers, and deeply nested attributes.
        Ignores integers (like line numbers) to prevent logic errors.
        """
        # 1. Base case: float or int
        if isinstance(prob_obj, float): return prob_obj
        if isinstance(prob_obj, int): return float(prob_obj)
        
        # 2. Try direct string conversion
        try: return float(str(prob_obj))
        except: pass

        # 3. Known Attribute Search
        for attr in ['value', 'token', 'number', 'constant', 'val']:
            if hasattr(prob_obj, attr):
                val = getattr(prob_obj, attr)
                if val is not prob_obj:
                    try: return self._resolve_prob(val)
                    except: pass

        # 4. Deep Scan for float attributes (ignoring generic integers)
        for attr in dir(prob_obj):
            if attr.startswith('_'): continue
            try:
                val = getattr(prob_obj, attr)
                if isinstance(val, float): return val
                if isinstance(val, str):
                    f = float(val)
                    if 0.0 <= f <= 1.0: return f
            except: continue

        # 5. Last Resort: Regex on string representation (e.g. <NumericConstant 0.5>)
        s = str(prob_obj)
        match = re.search(r'(\d+\.\d+(?:e-?\d+)?)', s)
        if match: return float(match.group(1))

        # Default fallback
        print(f"WARNING: Could not parse probability '{prob_obj}'. Defaulting to 1.0")
        return 1.0

    # --- TRANSLATION LOGIC ---
    def ground_state_variables(self):
        """Generates all possible grounded atoms (boolean variables) from domain predicates and objects."""
        for predicate in self.domain.predicates:
            param_types = [ptype.type_name for ptype in predicate.parameters]
            object_lists = [self._get_objects_for_type(t) for t in param_types]
            for args in itertools.product(*object_lists):
                atom_name = self._predicate_to_prism(predicate.name, args)
                self.ground_atoms.append(atom_name)
        self.ground_atoms = sorted(list(set(self.ground_atoms)))


    def _translate_expression(self, expr: Any, var_map: Dict[str, str]) -> str:
        """Recursively translates a PDDL logical expression (precondition/goal) into a PRISM boolean string."""
        if not expr: return "true"
        typename = type(expr).__name__.lower()
        
        # Handle Containers (AND / OR)
        children = self._get_list_content(expr)
        if children is not None:
            parts = [self._translate_expression(e, var_map) for e in children]
            if 'or' in typename or 'disjunct' in typename:
                return f"({' | '.join(parts)})" if parts else "false"
            return f"({' & '.join(parts)})" if parts else "true"
        
        # Handle Negation (NOT)
        if 'not' in typename or 'neg' in typename:
            child = self._get_child_content(expr)
            if child: return f"!({self._translate_expression(child, var_map)})"
            return "true"

        # Handle Atoms
        atom_data = self._get_atom_details(expr)
        if atom_data:
            pred_name, args = atom_data
            ground_args = [var_map.get(arg.name, arg.name) for arg in args]
            return self._predicate_to_prism(pred_name, ground_args)
        return "true"

    def _effect_to_assignments(self, effect: Any, var_map: Dict[str, str]) -> List[Tuple[str, str]]:
        """
        Recursively extracts deterministic or conditional updates from an effect object.
        Returns a list of tuples: (Variable, New_Value_Expression).
        """
        if not effect: return []
        typename = type(effect).__name__.lower()
        
        # If we hit a probabilistic block, stop recursion (handled by _process_effects).
        if 'prob' in typename or hasattr(effect, 'outcomes'): return [] 

        # 1. List of effects (AND)
        children = self._get_list_content(effect)
        if children is not None:
            assignments = []
            for e in children: assignments.extend(self._effect_to_assignments(e, var_map))
            return assignments

        # 2. Negation (Delete List) -> var' = false
        if 'not' in typename or 'neg' in typename:
            child = self._get_child_content(effect)
            if child:
                pos = self._effect_to_assignments(child, var_map)
                return [(k, "false") for k, _ in pos]
            return []

        # 3. Conditional Effect (WHEN condition effect) -> var' = (cond ? val : var)
        if 'when' in typename or 'cond' in typename:
            condition = getattr(effect, 'condition', None)
            inner_effect = getattr(effect, 'effect', None)
            if condition and inner_effect:
                cond_str = self._translate_expression(condition, var_map)
                inner_assigns = self._effect_to_assignments(inner_effect, var_map)
                # Apply ternary logic for PRISM update
                return [(var, f"({cond_str} ? {val} : {var})") for var, val in inner_assigns]
            return []

        # 4. Atomic Effect (Add List) -> var' = true
        atom_data = self._get_atom_details(effect)
        if atom_data:
            pred_name, args = atom_data
            ground_args = [var_map.get(arg.name, arg.name) for arg in args]
            atom = self._predicate_to_prism(pred_name, ground_args)
            return [(atom, "true")]
            
        return []

    def _process_effects(self, effects: Any, var_map: Dict[str, str]) -> Optional[List[Tuple[float, str]]]:
        """
        Processes action effects, handling both deterministic logic and probabilistic outcomes.
        Returns a list of (probability, update_string) tuples.
        """
        if not effects: return [(1.0, "true")]
        
        # Separate the "Base" effects (deterministic/conditional) from the "Probabilistic" effect.
        all_children = []
        container = self._get_list_content(effects)
        if container is not None: all_children = container
        else: all_children = [effects]

        base_effects = []
        prob_effect_obj = None

        for child in all_children:
            is_prob = False
            if hasattr(child, 'outcomes') or hasattr(child, 'outcome'): is_prob = True
            elif 'prob' in type(child).__name__.lower(): is_prob = True
            
            if is_prob: prob_effect_obj = child 
            else: base_effects.append(child)

        # Generate assignments for base effects
        base_assigns = []
        for b_eff in base_effects:
            base_assigns.extend(self._effect_to_assignments(b_eff, var_map))

        # Generate probabilistic outcomes (merging base effects into each outcome)
        final_outcomes = []
        if prob_effect_obj:
            outcomes = getattr(prob_effect_obj, 'outcomes', getattr(prob_effect_obj, 'outcome', []))
            total_prob = 0.0
            if outcomes:
                for outcome in outcomes:
                    p_val = 1.0
                    if hasattr(outcome, 'probability'):
                        p_val = self._resolve_prob(outcome.probability)
                    
                    total_prob += p_val
                    eff = getattr(outcome, 'effect', outcome)
                    outcome_assigns = self._effect_to_assignments(eff, var_map)
                    
                    final_outcomes.append((p_val, outcome_assigns + base_assigns))
            
            # Implicit remainder (if probabilities sum to < 1.0)
            if total_prob < (1.0 - 1e-6):
                final_outcomes.append((1.0 - total_prob, base_assigns))
        else:
            # If no probabilistic effect, treat as single 1.0 outcome
            final_outcomes.append((1.0, base_assigns))

        # Format as PRISM update strings
        results = []
        for prob, assigns in final_outcomes:
            state_map = {}
            for atom, val in assigns:
                state_map[atom] = val
            
            if not state_map:
                update_str = "true"
            else:
                parts = [f"({atom}' = {val})" for atom, val in state_map.items()]
                update_str = " & ".join(parts)
            results.append((prob, update_str))
        return results

    def ground_actions_logic(self):
        """Generates all grounded actions with guards and updates."""
        # Check if we are using the "Probabilistic Setup" pattern
        using_prob_setup = 'not_setup' in self.ground_atoms

        for action in self.domain.actions:
            param_names = [ptype.name for ptype in action.parameters]
            param_types = [ptype.type_name for ptype in action.parameters]
            object_lists = [self._get_objects_for_type(t) for t in param_types]

            for args in itertools.product(*object_lists):
                var_map = dict(zip(param_names, args))
                action_name = self._predicate_to_prism(action.name, list(args))
                guard = self._translate_expression(action.precondition, var_map)
                
                # Enforce ordering: All normal actions must wait for setup to complete.
                if using_prob_setup and action.name != 'prob_setup_init':
                    guard = f"({guard}) & !not_setup"

                updates = self._process_effects(action.effect, var_map)
                
                if updates is not None:
                    self.ground_actions.append({"name": action_name, "guard": guard, "updates": updates})

        self.action_update_map = {action['name']: action['updates'] for action in self.ground_actions}

    def _write_initial_state(self) -> List[str]:
        """Writes the variables block for PRISM, setting initial values."""
        lines = []
        init_facts = set()
        for atom in self.problem.initial:
            args = [arg.name for arg in atom.arguments]
            init_facts.add(self._predicate_to_prism(atom.name, args))
        for atom in self.ground_atoms:
            val = "true" if atom in init_facts else "false"
            lines.append(f"\t{atom} : bool init {val};")
        return lines

    def generate_goal_label(self) -> str:
        """Generates the PRISM goal label from the problem definition."""
        if not self.problem.goal: return ""
        goal_expr = self._translate_expression(self.problem.goal, {})
        return f'label "goal" = {goal_expr};'

    def generate_mdp(self) -> str:
        """Assembles the full PRISM MDP file."""
        lines = ["mdp", "", "module main"]
        lines.extend(self._write_initial_state())
        lines.append("")
        
        # Write actions
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

        lines.extend(self._write_initial_state())

        # write rules from policy
        for rule in policy:
            guard = rule['if']

            def parse_guard_predicates(guard: str):
                """
                Given a guard string like 'on_1_2 & clear_1 & handempty_ & pick-up_1',
                return a dict mapping predicate names to lists of their arguments as strings.
                """
                predicate_strs = [pred.strip().rstrip('_') for pred in guard.split('&')]
                predicate_args_map = {}
                for pred in predicate_strs:
                    match = re.match(r'([a-zA-Z\-]+)((?:_\d+)*)$', pred)
                    if match:
                        name = match.group(1)
                        args_section = match.group(2)
                        args = [arg for arg in args_section.split('_') if arg]
                        predicate_args_map[name] = args
                    else:
                        predicate_args_map[pred] = []
                return predicate_args_map
            
            pred_args_map = parse_guard_predicates(guard)
            all_args = [int(arg) for args in pred_args_map.values() for arg in args if arg.isdigit()]
            max_arity = max(all_args) if all_args else 0

            # search predicate by name to assign types to arguments
            argument_types = ["object" for _ in range(max_arity)]
            for pred_name, args in pred_args_map.items():
                pred = self.name_to_pred_map[pred_name]
                for i, arg in enumerate(args):
                    argument_types[int(arg) - 1] = pred.parameters[i].type_name
            object_lists = [self._get_objects_for_type(t) for t in argument_types]

            # replace dashes with underscores in the guard string
            guard = guard.replace('-', '_')

            print('object_lists:', object_lists)
            for args in itertools.product(*object_lists):
                # Assume arg_map is now a character-to-character mapping, e.g. {'x':'a', 'y':'b'}
                # Replace all occurrences of each variable character in the guard and then strings
                def apply_arg_map(s, arg_map):
                    for var, val in arg_map.items():
                        # Just replace any occurrence of _var with _val (no need to check for trailing underscore)
                        s = s.replace(f"_{var}", f"_{val}")
                    return s

                arg_map = {i+1:arg for i, arg in enumerate(args)}
                grounded_guard = apply_arg_map(guard, arg_map)
                grounded_action = apply_arg_map(rule['then'], arg_map)

                grounded_action = grounded_action.replace('-', '_')
                if grounded_action not in self.action_update_map.keys():
                    continue

                print('GROUNDED_ACTION:', grounded_action)
                print('GROUNDED_GUARD:', grounded_guard)
                action_update = self.action_update_map[grounded_action] # CHECK THIS
                action_update_str = " + ".join([f"{prob} : {update}" for prob, update in action_update])

                rule_line = f"\t[{rule['name']}] {grounded_guard} -> {action_update_str};"
                lines.append(rule_line)

        lines.append("endmodule")
        lines.append("")
        
        # Write Goal Label
        if (g := self.generate_goal_label()): lines.append(g)
        return "\n".join(lines)

def pddl_to_mdp(domain_file: str, problem_file: str) -> Tuple[str, PPDDLToPRISM]:
    translator = PPDDLToPRISM(domain_file, problem_file)
    translator.ground_state_variables()
    translator.ground_actions_logic()
    return translator.generate_mdp(), translator

if __name__ == "__main__":
    mdp_str, _ = pddl_to_mdp("data/stochastic/bomb-in-toilet/domain.pddl", "data/stochastic/bomb-in-toilet/3.pddl")
    print("----- Generated MDP -----")
    print(mdp_str)
    with open("tmp/generated_mdp.prism", "w") as f:
        f.write(mdp_str)