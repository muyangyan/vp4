import os
from fire import Fire
from run import run_single

def main(
    domain_dir: str = "data/deterministic/blocksworld",
):
    problem_files = [f for f in os.listdir(domain_dir) if f.endswith(".pddl")]
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
                print('RUNNING FOR:', problem_file, policy_file, property_file)
                result = run_single(domain_dir, problem_file, policy_file, property_file)
                results[policy_file][problem_file][property_file] = result
    
    print(f"\nResults for domain `{domain_dir}`")
    for policy_file in policy_files:
        print(f"Policy `{policy_file}`:")
        for property_file in property_files:
            print(f"\t| {property_file.split(".pctl")[0]}", end="")
        print("")

        for problem_file in problem_files:
            print(f"{problem_file}", end="")
            for property_file in property_files:
                print(f"\t| {results[policy_file][problem_file][property_file]}", end="")
            print("")

    return

if __name__ == "__main__":
    Fire(main)
