import os
from fire import Fire
from run import run_single

def main(
    domain_dir: str = "data/deterministic/blocksworld",
):
    problem_files = [f for f in os.listdir(domain_dir) if f.endswith(".pddl")]
    if "domain.pddl" in problem_files:
        problem_files.remove("domain.pddl")
    
    policy_files = [f for f in os.listdir(domain_dir) if f.endswith(".json")]
    property_files = [f for f in os.listdir(domain_dir) if f.endswith(".pctl")]

    problem_files = sorted(problem_files)
    policy_files = sorted(policy_files)
    property_files = sorted(property_files)

    print('DOMAIN DIR:', domain_dir)
    print(problem_files)
    print(policy_files)
    print(property_files)

    results = {}

    for policy_file in policy_files:
        results[policy_file] = {}
        for problem_file in problem_files:
            results[policy_file][problem_file] = {}
            for property_file in property_files:
                print(f'RUNNING FOR: {problem_file} {policy_file} {property_file}')
                res = run_single(domain_dir, problem_file, policy_file, property_file)
                results[policy_file][problem_file][property_file] = res if res is not None else "Error"
    
    # --- Formatting Logic ---
    print(f"\nResults for domain `{domain_dir}`")
    
    # Calculate column widths
    # 1. First column width = max length of problem filenames (or at least 15 chars)
    if problem_files:
        col0_width = max(len(p) for p in problem_files) + 4
    else:
        col0_width = 15
        
    # 2. Property column widths = max length of property name (or at least 10 chars)
    # We strip .pctl for the header name
    prop_names = [p.split('.pctl')[0] for p in property_files]
    prop_widths = [max(len(n), 10) + 2 for n in prop_names]

    for policy_file in policy_files:
        print(f"Policy `{policy_file}`:")
        
        # Print Header Row
        # Empty block for the "Problem" column
        print(f"{'':<{col0_width}}", end="")
        for i, name in enumerate(prop_names):
            print(f"| {name:<{prop_widths[i]}}", end="")
        print("|")
        
        # Print Separator Line
        total_width = col0_width + sum(w + 2 for w in prop_widths) + len(prop_widths) # rough estimate
        print("-" * total_width)

        # Print Data Rows
        for problem_file in problem_files:
            print(f"{problem_file:<{col0_width}}", end="")
            for i, property_file in enumerate(property_files):
                val = str(results[policy_file][problem_file][property_file])
                print(f"| {val:<{prop_widths[i]}}", end="")
            print("|")
        print("\n")

    return

if __name__ == "__main__":
    Fire(main)