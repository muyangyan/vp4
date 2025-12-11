from fire import Fire
import json
import subprocess
from translation import pddl_to_mdp
from typing import Optional
import os

def verify_property(dtmc_file: str, property_file: str) -> Optional[str]:
    """
    dtmc_file: Path to the DTMC model file in PRISM format.
    property_file: path to file containing property in 
    """
    # call prism on dtmc file, with property speicified in the file
    with open(property_file, "r") as property_infile:
        property = property_infile.read().strip()

    results_file = "tmp/results.txt"
    if not os.path.exists(results_file):
        with open(results_file, "w") as f:
            f.write("")

    # Prepare command for subprocess
    command = ["prism", dtmc_file, "-pctl", f"P=? [{property}]", f"-exportresults", f"{results_file}"]
    output_data = subprocess.run(command, capture_output=True, text=True)

    # Check return code
    if output_data.returncode != 0:
        print(f"PRISM returned {output_data.returncode} on inputs `{command}` with info:\n--- stdout ---\n{output_data.stdout}\n--- stderr ---\n{output_data.stderr}\nAborting verify_property.")
        return None
    
    with open(results_file, "r") as results_infile:
        results_raw = results_infile.read().strip()
        output_amount = results_raw.split()[1].strip()

    return output_amount


def run_single(
    domain_dir: str = "data/deterministic/blocksworld/",
    problem_file: str = "1.pddl",
    policy_file: str = "all_on_table.json", 
    property_file: str = "property.pctl",
    run_prism: str = "True",
):
    # parse pddl domain, problem -> mdp file =========================
    domain_file = os.path.join(domain_dir, "domain.pddl")
    problem_file = os.path.join(domain_dir, problem_file)
    policy_file = os.path.join(domain_dir, policy_file)
    property_file = os.path.join(domain_dir, property_file)
    mdp_text, translator = pddl_to_mdp(domain_file, problem_file)
    os.makedirs("tmp/", exist_ok=True)
    with open("tmp/mdp.prism", "w") as f:
        f.write(mdp_text)

    # apply policy to get actions -> dtmc file =======================
    with open(policy_file, "r") as f:
        policy = json.load(f)

    dtmc_text = translator.generate_dtmc(policy)

    with open("tmp/dtmc.prism", "w") as f:
        f.write(dtmc_text)

    # call prism on dtmc file, with property, if provided ============
    if run_prism != "True":
        return

    print(f"Verifying property using generated dtmc...")
    result = verify_property("tmp/dtmc.prism", property_file)

    # print result
    print(f"Result for problem `{problem_file}`, policy `{policy_file}`, property `{property_file}`: ")
    print(result)
    return

if __name__ == "__main__":
    Fire(run_single)
