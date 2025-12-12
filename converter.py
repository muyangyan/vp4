import re
import json

class PrismMDPToDTMC:
    def __init__(self, mdp_file: str, policy_file: str):
        with open(mdp_file, 'r') as f:
            self.mdp_lines = f.readlines()
        with open(policy_file, 'r') as f:
            self.policy = json.load(f)

    def _sanitize(self, name: str) -> str:
        return name.replace('-', '_').replace(' ', '_')

    def convert(self) -> str:
        dtmc_lines = []
        # Header switch
        if self.mdp_lines and self.mdp_lines[0].strip() == "mdp":
            dtmc_lines.append("dtmc\n")
        else:
            dtmc_lines.append("dtmc\n")

        # Regex to parse MDP transitions: [action] guard -> update;
        trans_pattern = re.compile(r'^\s*\[([^\]]+)\]\s*(.+?)\s*->\s*(.+?);\s*$')
        
        # Build policy map: action_name -> list of guards
        # Policy action names often use dashes; MDP uses underscores. We match on sanitized names.
        policy_map = {}
        for rule in self.policy:
            sanitized_action = self._sanitize(rule['then'])
            guard = self._sanitize(rule['if']) # PDDL vars also need sanitization if they have dashes
            if sanitized_action not in policy_map:
                policy_map[sanitized_action] = []
            policy_map[sanitized_action].append(guard)

        for line in self.mdp_lines[1:]:
            line_strip = line.strip()
            
            # Pass through non-transition lines (vars, endmodule, labels)
            match = trans_pattern.match(line_strip)
            if not match:
                dtmc_lines.append(line)
                continue

            action_name = match.group(1)
            mdp_guard = match.group(2)
            update = match.group(3)

            # RULE 1: Preserve Setup/Nature Actions
            if action_name == "prob_setup_init":
                dtmc_lines.append(line)
                continue

            # RULE 2: Apply Policy
            # If this action is in the policy, we restrict its guard.
            # If it is NOT in the policy, we drop it (by not appending).
            if action_name in policy_map:
                policy_guards = policy_map[action_name]
                # Combined policy guard: (g1) | (g2) ...
                combined_p_guard = " | ".join([f"({g})" for g in policy_guards])
                
                # New transition: [] (MDP_Guard) & (Policy_Guard) -> Update
                # We remove the action label (make it empty []) for the DTMC or keep it for tracing.
                # PRISM DTMCs can have labeled transitions, but usually [] is cleaner for determinism checks.
                # However, to avoid "Multiple overlapping actions" errors if we have duplicate guards,
                # let's keep the label but make it unique or just keep the original label.
                
                new_line = f"\t[{action_name}] ({mdp_guard}) & ({combined_p_guard}) -> {update};\n"
                dtmc_lines.append(new_line)

        return "".join(dtmc_lines)

def convert_mdp_to_dtmc(mdp_path: str, policy_path: str) -> str:
    converter = PrismMDPToDTMC(mdp_path, policy_path)
    return converter.convert()