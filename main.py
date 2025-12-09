from fire import Fire


def pddl_to_mdp(domain_file: str, problem_file: str) -> str:
    return ""


def mdp_to_dtmc(mdp_file: str, policy: str) -> str:
    return ""

def verify_property(dtmc_file: str, property: str) -> str:
    """
    dtmc_file: Path to the DTMC model file in PRISM format.
    property: path to file containing property in 
    """
    # call prism on dtmc file, with property

    return ""



def run_single(
    domain_file: str,
    problem_file: str,
    policy: str, 
    property: str
):


    # parse pddl domain, problem -> mdp file
    mdp_text = pddl_to_mdp(domain_file, problem_file)
    # write mdp file to disk
    with open("tmp/mdp.prism", "w") as f:
        f.write(mdp_text)


    # apply policy to get actions -> dtmc file
    dtmc_text = mdp_to_dtmc(mdp_text, policy)
    # write dtmc file to disk
    with open("tmp/dtmc.prism", "w") as f:
        f.write(dtmc_text)

    # call prism on dtmc file, with property
    result = verify_property("tmp/dtmc.prism", property)

    # print result
    print(result)

def main():
    pass


if __name__ == "__main__":
    Fire(run_single)