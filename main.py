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

    print('DOMAIN DIR:', domain_dir)
    print(problem_files)
    print(policy_files)
    print(property_files)

    for problem_file in problem_files:
        for policy_file in policy_files:
            for property_file in property_files:
                print('RUNNING FOR:', problem_file, policy_file, property_file)
                result = run_single(domain_dir, problem_file, policy_file, property_file)
    
if __name__ == "__main__":
    Fire(main)

