from fire import Fire
import json
import plado
import subprocess
from src.pddl_parser import PDDLToPRISM




def verify_property(dtmc_file: str, property_file: str) -> str:
    """
    dtmc_file: Path to the DTMC model file in PRISM format.
    property_file: path to file containing property in 
    """
    # call prism on dtmc file, with property speicified in the file
    with open(property_file, "r") as property_infile:
        property = property_infile.read().strip()

    # TODO -- change tmp/results.txt to wherever it should be instead
    results_file = "tmp/results.txt"

    # Prepare command for subprocess
    command = ["prism", dtmc_file, "-pctl", f"$'Pmax=? [{property}]'", f"-exportresults {results_file}"]
    output_data = subprocess.run(command, capture_output=True, text=True)

    # Check return code
    if output_data.returncode != 0:
        print(f"PRISM returned {output_data.returncode} on inputs `{command}` with error:\n{output_data.stderr}\nAborting verify_property.")
        return output_data.stderr
    
    # TODO perform post-processing:
    # - Perform error checking (e.g. the model may be incomplete, or there may be warnings about its structure, or certain states are unreachable or unactionable)
    # - Return results if there are no errors

    # Get command output (if needed)
    # output_str = output_data.stdout
    
    # Get results from results file
    # Note: results files are output as "Result\nn.nn\n", hence we only need the second line
    with open(results_file, "r") as results_infile:
        results_raw = results_infile.read().strip()
        output_amount = results_raw.split()[1].strip()

    return output_amount


def run_single(
    domain_file: str = "data/deterministic/blocksworld/domain.pddl",
    problem_file: str = "data/deterministic/blocksworld/1.pddl",
    policy_file: str = "data/deterministic/blocksworld/policy.json", 
    property_file: str = "data/deterministic/blocksworld/property.pctl",
):

    translator = PDDLToPRISM(domain_file, problem_file)

    # parse pddl domain, problem -> mdp file =========================
    translator.ground_state_variables()
    translator.ground_actions_logic()

    mdp_text = translator.generate_mdp()

    with open("tmp/mdp.prism", "w") as f:
        f.write(mdp_text)


    # apply policy to get actions -> dtmc file =======================
    with open(policy_file, "r") as f:
        policy = json.load(f)

    dtmc_text = translator.generate_dtmc(policy)

    with open("tmp/dtmc.prism", "w") as f:
        f.write(dtmc_text)

    # call prism on dtmc file, with property =========================
    result = verify_property("tmp/dtmc.prism", property_file)

    # print result
    print(result)

def main():
    pass


if __name__ == "__main__":
    Fire(run_single)
