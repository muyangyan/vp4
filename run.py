from fire import Fire
import json
import subprocess
from translation import pddl_to_mdp
from typing import Optional
import os

def verify_property(dtmc_file: str, property_file: str) -> Optional[str]:
    with open(property_file, "r") as property_infile:
        property = property_infile.read().strip()

    results_file = "tmp/results.txt"
    if not os.path.exists(results_file):
        with open(results_file, "w") as f:
            f.write("")

    # Removed -fixdeadlocks to support older PRISM versions / standard usage
    command = ["prism", dtmc_file, "-pctl", f"P=? [{property}]", "-exportresults", f"{results_file}"]
    output_data = subprocess.run(command, capture_output=True, text=True)

    if output_data.returncode != 0:
        print(f"PRISM returned {output_data.returncode} on inputs `{command}` with info:\n--- stdout ---\n{output_data.stdout}\n--- stderr ---\n{output_data.stderr}\nAborting verify_property.")
        return None
    
    with open(results_file, "r") as results_infile:
        try:
            results_raw = results_infile.read().strip()
            output_amount = results_raw.split()[1].strip()
        except IndexError:
            return "Error (No Result)"

    return output_amount


def run_single(
    domain_dir: str = "data/deterministic/blocksworld/",
    problem_file: str = "1.pddl",
    policy_file: str = "all_on_table.json", 
    property_file: str = "property.pctl",
    run_prism: str = "True",
):
    # 1. PDDL -> MDP
    domain_file_path = os.path.join(domain_dir, "domain.pddl")
    problem_file_path = os.path.join(domain_dir, problem_file)
    policy_file_path = os.path.join(domain_dir, policy_file)
    property_file_path = os.path.join(domain_dir, property_file)
    
    mdp_text, translator = pddl_to_mdp(domain_file_path, problem_file_path)
    os.makedirs("tmp/", exist_ok=True)
    with open("tmp/mdp.prism", "w") as f:
        f.write(mdp_text)

    # 2. MDP + Policy -> DTMC (using translator)
    with open(policy_file_path, "r") as f:
        policy = json.load(f)

    dtmc_text = translator.generate_dtmc(policy)

    with open("tmp/dtmc.prism", "w") as f:
        f.write(dtmc_text)

    # 3. Verify
    if run_prism != "True":
        return

    print(f"Verifying property using generated dtmc...")
    result = verify_property("tmp/dtmc.prism", property_file_path)

    print(f"Result for problem `{problem_file}`, policy `{policy_file}`, property `{property_file}`: ")
    print(result)
    return

if __name__ == "__main__":
    Fire(run_single)