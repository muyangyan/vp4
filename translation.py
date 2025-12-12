import re
import tempfile
import os
import itertools
from typing import List, Dict, Tuple, Any, Optional

# --- PLADO IMPORT & MONKEY PATCH ---
import plado.parser

def _dummy_make_checks(domain, problem, file=None):
    return False

if hasattr(plado.parser, 'sanity_checks'):
    plado.parser.sanity_checks.make_checks = _dummy_make_checks
plado.parser.make_checks = _dummy_make_checks

from plado.parser import parse


class PPDDLToPRISM:
    def __init__(self, domain_file: str, problem_file: str):
        print(f"--- PREPROCESSING: {problem_file} ---")
        self.clean_domain, self.clean_problem = self._preprocess(domain_file, problem_file)

        try:
            self.domain_file = self.clean_domain
            self.problem_file = self.clean_problem
            self.domain, self.problem = parse(self.clean_domain, self.clean_problem)
        finally:
            pass

        self.objects = self._collect_objects()
        self.ground_atoms = []
        self.ground_actions = []
        self.name_to_pred_map = {n:p for n, p in zip([p.name for p in self.domain.predicates], self.domain.predicates)}

    def _preprocess(self, d_path, p_path):
        with open(d_path, 'r') as f: d_text = f.read()
        with open(p_path, 'r') as f: p_text = f.read()

        p_text = re.sub(r'\(:requirements[^)]+\)', '', p_text)

        init_data = self._extract_balanced_block(p_text, '(:init')
        if init_data and 'probabilistic' in init_data[2]:
            print("  [Preprocessor] Converting Probabilistic Init to 'Probabilistic Setup' action...")
            start, end, init_block = init_data
            prob_data = self._extract_balanced_block(init_block, 'probabilistic')
            
            if prob_data:
                inner_prob = prob_data[2].replace('(probabilistic', '', 1).strip()[:-1]
                new_init = "(:init (not-setup))"
                p_text = p_text[:start] + new_init + p_text[end:]
                
                if '(:predicates' in d_text:
                    d_text = d_text.replace('(:predicates', '(:predicates (not-setup)')
                
                setup_action = f"\n(:action prob_setup_init :parameters () :precondition (not-setup) :effect (and (not (not-setup)) (probabilistic {inner_prob})))\n"
                
                d_text = d_text.strip()
                last_paren = d_text.rfind(')')
                if last_paren != -1:
                    d_text = d_text[:last_paren] + setup_action + ")"
                else:
                    d_text += setup_action

        def write_tmp(content, suffix):
            tf = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
            tf.write(content)
            tf.close()
            return tf.name
            
        return write_tmp(d_text, "domain_fixed.pddl"), write_tmp(p_text, "problem_fixed.pddl")

    def _extract_balanced_block(self, text, start_keyword):
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
        clean_pred = predicate.replace('-', '_')
        if not args: return clean_pred
        clean_args = [a.replace('-', '_') for a in args]
        return f"{clean_pred}_{'_'.join(clean_args)}"

    def _get_list_content(self, obj: Any) -> Optional[List[Any]]:
        for attr in ['outcomes', 'effects', 'sub_formulas', 'parts', 'children', 'operands', 'effect_list']:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                if isinstance(val, (list, tuple)): return val
        return None

    def _get_child_content(self, obj: Any) -> Any:
        candidates = ['atom', 'expression', 'operand', 'effect', 'argument', 'op', 'condition', 'formula', 'prop']
        for attr in candidates:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                if val is not None: return val
        for attr in dir(obj):
            if attr.startswith('_'): continue
            val = getattr(obj, attr)
            if hasattr(val, 'name') or hasattr(val, 'predicate') or hasattr(val, 'op') or hasattr(val, 'sub_formulas'):
                return val
        return None

    def _get_atom_details(self, obj: Any) -> Optional[Tuple[str, List[Any]]]:
        if hasattr(obj, 'name') and hasattr(obj, 'arguments'): return obj.name, obj.arguments
        elif hasattr(obj, 'predicate'): return obj.predicate.name, getattr(obj, 'arguments', [])
        return None

    def _resolve_prob(self, prob_obj: Any) -> float:
        if isinstance(prob_obj, float): return prob_obj
        if isinstance(prob_obj, int): return float(prob_obj)
        if isinstance(prob_obj, str):
            if '/' in prob_obj:
                try:
                    n, d = prob_obj.split('/')
                    return float(n) / float(d)
                except: pass
            try: return float(prob_obj)
            except: pass

        op = getattr(prob_obj, 'op', None) or getattr(prob_obj, 'operator', None)
        op_str = str(op) if op else ""
        children = getattr(prob_obj, 'children', None) or getattr(prob_obj, 'operands', None)
        if children and len(children) == 2 and ('/' in op_str or 'div' in op_str.lower()):
            left = self._resolve_prob(children[0])
            right = self._resolve_prob(children[1])
            if right != 0: return left / right

        search_space = ['token', 'value', 'number', 'constant', 'val', 'text', 'string']
        if hasattr(prob_obj, '__dict__'):
            search_space.extend(prob_obj.__dict__.keys())
            
        for attr in search_space:
            if attr.startswith('_'): continue
            if hasattr(prob_obj, attr):
                val = getattr(prob_obj, attr)
                if val is not prob_obj and val is not None:
                    if isinstance(val, (float, int)): return float(val)
                    if isinstance(val, str):
                        try: return float(val)
                        except: pass
                    if hasattr(val, 'text'):
                        try: return self._resolve_prob(val.text)
                        except: pass
                    if not isinstance(val, (list, tuple, dict)):
                        try:
                            ret = self._resolve_prob(val)
                            if ret != 1.0: return ret
                        except: pass

        s = str(prob_obj)
        frac_match = re.search(r'(\d+)\s*/\s*(\d+)', s)
        if frac_match:
            return float(frac_match.group(1)) / float(frac_match.group(2))
        match = re.search(r'(\d+\.\d+(?:e-?\d+)?)', s)
        if match: return float(match.group(1))
        
        print(f"WARNING: Parsing failed for '{prob_obj}' (Type: {type(prob_obj)}). Defaulting to 1.0")
        return 1.0

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
        
        children = self._get_list_content(expr)
        if children is not None:
            parts = [self._translate_expression(e, var_map) for e in children]
            if 'or' in typename or 'disjunct' in typename:
                return f"({' | '.join(parts)})" if parts else "false"
            return f"({' & '.join(parts)})" if parts else "true"
        
        if 'not' in typename or 'neg' in typename:
            child = self._get_child_content(expr)
            if child: return f"!({self._translate_expression(child, var_map)})"
            return "true"

        atom_data = self._get_atom_details(expr)
        if atom_data:
            pred_name, args = atom_data
            ground_args = [var_map.get(arg.name, arg.name) for arg in args]
            return self._predicate_to_prism(pred_name, ground_args)
        return "true"

    def _effect_to_assignments(self, effect: Any, var_map: Dict[str, str]) -> List[Tuple[str, str]]:
        if not effect: return []
        typename = type(effect).__name__.lower()
        if 'prob' in typename or hasattr(effect, 'outcomes'): return [] 

        children = self._get_list_content(effect)
        if children is not None:
            assignments = []
            for e in children: assignments.extend(self._effect_to_assignments(e, var_map))
            return assignments

        if 'not' in typename or 'neg' in typename:
            child = self._get_child_content(effect)
            if child:
                pos = self._effect_to_assignments(child, var_map)
                return [(k, "false") for k, _ in pos]
            return []

        if 'when' in typename or 'cond' in typename:
            condition = getattr(effect, 'condition', None)
            inner_effect = getattr(effect, 'effect', None)
            if condition and inner_effect:
                cond_str = self._translate_expression(condition, var_map)
                inner_assigns = self._effect_to_assignments(inner_effect, var_map)
                return [(var, f"({cond_str} ? {val} : {var})") for var, val in inner_assigns]
            return []

        atom_data = self._get_atom_details(effect)
        if atom_data:
            pred_name, args = atom_data
            ground_args = [var_map.get(arg.name, arg.name) for arg in args]
            atom = self._predicate_to_prism(pred_name, ground_args)
            return [(atom, "true")]
        return []

    def _process_effects(self, effects: Any, var_map: Dict[str, str]) -> Optional[List[Tuple[float, str]]]:
        if not effects: return [(1.0, "true")]
        
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

        base_assigns = []
        for b_eff in base_effects:
            base_assigns.extend(self._effect_to_assignments(b_eff, var_map))

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
            
            if total_prob < (1.0 - 1e-6):
                final_outcomes.append((1.0 - total_prob, base_assigns))
        else:
            final_outcomes.append((1.0, base_assigns))

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
        using_prob_setup = 'not_setup' in self.ground_atoms

        for action in self.domain.actions:
            param_names = [ptype.name for ptype in action.parameters]
            param_types = [ptype.type_name for ptype in action.parameters]
            object_lists = [self._get_objects_for_type(t) for t in param_types]

            for args in itertools.product(*object_lists):
                var_map = dict(zip(param_names, args))
                action_name = self._predicate_to_prism(action.name, list(args))
                guard = self._translate_expression(action.precondition, var_map)
                
                if using_prob_setup and action.name != 'prob_setup_init':
                    guard = f"({guard}) & !not_setup"

                updates = self._process_effects(action.effect, var_map)
                
                if updates is not None:
                    self.ground_actions.append({"name": action_name, "guard": guard, "updates": updates})

        self.action_update_map = {action['name']: action['updates'] for action in self.ground_actions}

    def _write_initial_state(self) -> List[str]:
        lines = []
        init_facts = set()
        for atom in self.problem.initial:
            args = [arg.name for arg in atom.arguments]
            init_facts.add(self._predicate_to_prism(atom.name, args))
        
        # NOTE: Removed 'done' variable to allow multiple steps/loops
        
        for atom in self.ground_atoms:
            val = "true" if atom in init_facts else "false"
            lines.append(f"\t{atom} : bool init {val};")
        return lines

    def generate_goal_label(self) -> str:
        if not self.problem.goal: return ""
        goal_expr = self._translate_expression(self.problem.goal, {})
        return f'label "goal" = {goal_expr};'

    def generate_mdp(self) -> str:
        lines = ["mdp", "", "module main"]
        lines.extend(self._write_initial_state())
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
        lines.extend(self._write_initial_state())

        if "not_setup" in self.ground_atoms and "prob_setup_init" in self.action_update_map:
            setup_updates = self.action_update_map["prob_setup_init"]
            setup_str = " + ".join([f"{prob} : {update}" for prob, update in setup_updates])
            lines.append(f"\t[prob_setup_init] not_setup -> {setup_str};")
            
        used_guards = []
        
        for rule in policy:
            guard_str = rule['if']
            action_str = rule['then']
            rule_name = rule['name'].replace('-', '_').replace(' ', '_')

            def get_vars(s: str) -> List[int]:
                return [int(x) for x in re.findall(r'_(\d+)\b', s)]

            guard_vars = get_vars(guard_str)
            action_vars = get_vars(action_str)
            all_vars = set(guard_vars + action_vars)
            
            # Removed !done check to allow looping
            setup_guard = "& !not_setup" if "not_setup" in self.ground_atoms else ""

            if not all_vars:
                clean_action = action_str.replace('-', '_')
                if clean_action in self.action_update_map:
                    updates = self.action_update_map[clean_action]
                    # Removed done'=true update
                    update_str = " + ".join([f"{p} : {u}" for p, u in updates])
                    clean_guard = guard_str.replace('-', '_') 
                    
                    full_guard = f"{clean_guard} {setup_guard}"
                    lines.append(f"\t[{rule_name}] {full_guard} -> {update_str};")
                    used_guards.append(f"({clean_guard})")
                continue

            max_arity = max(all_vars)
            argument_types = ["object" for _ in range(max_arity)]

            def parse_guard_predicates(g_str):
                atoms = re.split(r'[&|!()]', g_str)
                mapping = {}
                for atom in atoms:
                    atom = atom.strip()
                    if not atom: continue
                    match = re.match(r'^([a-zA-Z0-9\-]+)((?:_\d+)*)$', atom)
                    if match:
                        name = match.group(1)
                        arg_chunk = match.group(2)
                        args = [a for a in arg_chunk.split('_') if a]
                        mapping[name] = args
                return mapping

            pred_args_map = parse_guard_predicates(guard_str)
            for p_name, p_args in pred_args_map.items():
                pred_def = self.name_to_pred_map.get(p_name) or self.name_to_pred_map.get(p_name.replace('-', '_'))
                if pred_def:
                    for i, arg_idx_str in enumerate(p_args):
                        if arg_idx_str.isdigit():
                            idx = int(arg_idx_str) - 1
                            if 0 <= idx < max_arity:
                                argument_types[idx] = pred_def.parameters[i].type_name

            act_match = re.match(r'^([a-zA-Z0-9\-]+)((?:_\d+)*)$', action_str)
            if act_match:
                act_name = act_match.group(1)
                act_args = [a for a in act_match.group(2).split('_') if a]
                action_param_map = {a.name: [p.type_name for p in a.parameters] for a in self.domain.actions}
                param_types = action_param_map.get(act_name)
                if param_types and len(act_args) == len(param_types):
                    for i, arg_idx_str in enumerate(act_args):
                        if arg_idx_str.isdigit():
                            idx = int(arg_idx_str) - 1
                            if 0 <= idx < max_arity and argument_types[idx] == "object":
                                argument_types[idx] = param_types[i]

            object_lists = [self._get_objects_for_type(t) for t in argument_types]
            
            for args in itertools.product(*object_lists):
                arg_map = {str(i+1): obj for i, obj in enumerate(args)}
                sorted_vars = sorted(arg_map.keys(), key=len, reverse=True)

                grounded_guard = guard_str
                grounded_action = action_str

                for v in sorted_vars:
                    val = arg_map[v]
                    grounded_guard = grounded_guard.replace(f"_{v}", f"_{val}")
                    grounded_action = grounded_action.replace(f"_{v}", f"_{val}")

                grounded_action = grounded_action.replace('-', '_')
                grounded_guard = grounded_guard.replace('-', '_')

                if grounded_action not in self.action_update_map:
                    continue

                action_update = self.action_update_map[grounded_action]
                # Removed done'=true update
                update_str = " + ".join([f"{p} : {u}" for p, u in action_update])
                
                full_guard = f"{grounded_guard} {setup_guard}"
                lines.append(f"\t[{rule_name}] {full_guard} -> {update_str};")
                used_guards.append(f"({grounded_guard})")

        # 2. Add Catch-All (Stuck) Transition [Self-Loop]
        # Fires if not setup and NO user rule matches.
        if used_guards:
            negated_policies = " & ".join([f"!{g}" for g in used_guards])
            setup_guard = "& !not_setup" if "not_setup" in self.ground_atoms else ""
            lines.append(f"\t[stuck] {negated_policies} {setup_guard} -> 1.0 : true;")
        
        lines.append("endmodule")
        lines.append("")
        
        if (g := self.generate_goal_label()): lines.append(g)
        
        print('Done generating dtmc')
        return "\n".join(lines)

def pddl_to_mdp(domain_file: str, problem_file: str) -> Tuple[str, PPDDLToPRISM]:
    translator = PPDDLToPRISM(domain_file, problem_file)
    translator.ground_state_variables()
    translator.ground_actions_logic()
    return translator.generate_mdp(), translator