import argparse

import em.tools.input_output as IO


def register_parser(subparsers):
    parser = subparsers.add_parser('extract', usage=usage(), description=description())
    add_arguments(parser)


def add_arguments(parser):
    parser.add_argument("--input", metavar="FILE", help="Input File.", required=True)
    parser.add_argument("--chains", action="store_true", help="Extract PDBs by groups of chains using chain identifiers.")
    parser.add_argument("--models", action="store_true", help="Extract all models to separate outputs. No need to specify groups")
    parser.add_argument("--groups", type=str,help="""Chain groups to be extracted together as separate PDBs. User must specify
                                                     the chains to be output together to each PDB. There is no checking for
                                                     completeness. Ex: \"ABC,DEF\" will output two pdbs from a CIF with six
                                                     chains, or \"AB,CD,EF\" will output three pdbs from a CIF with six chains.""")
    parser.set_defaults(func=run)


def run(options):
    IO.PDBs_from_CIF(options.input,options.models,options.chains,options.groups)


def description():
    return """It extracts models or chain groups in the structure to separate PDB files,
              and it also gets rid of unwanted HETEROATOMS if they have a different chain identifier."""


def usage():
    return '\npdb_cif.py extract --input 1BRS.pdb --chains --groups AB,CD,EF\n' \
           'pdb_cif.py extract --input 1BRS.pdb --models'


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=description())
    add_arguments(arg_parser)
    args = arg_parser.parse_args()
    args.func(args)
