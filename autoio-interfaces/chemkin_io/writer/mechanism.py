"""
Write various parts of a Chemkin mechanism file
"""

from chemkin_io.writer import reaction
from chemkin_io.writer import thermo
from chemkin_io.writer import spc


def write_chemkin_file(elem_tuple=None, mech_spc_dct=None, spc_nasa7_dct=None,
                       rxn_param_dct=None, rxn_cmts_dct=None):
    """ Writes a Chemkin-formatted mechanism and/or thermo file as a string

        :param elem_tuple: tuple containing the element names
        :type elem_tuple: tuple
        :param mech_spc_dct: species data for a mechanism
        :type mech_spc_dct: {spc_name:data}
        :param spc_nasa7_dct: containing NASA-7 thermo data for each species
        :type spc_nasa7_dct: {spc_name:NASA-7 parameters}
        :param rxn_param_dct: containing the reaction parameters
        :type rxn_param_dct: {rxn:params}
        :param rxn_cmts_dct: comment information for each reaction
        :type rxn_cmts_dct: dict {rxn: cmts_dct}
        :return total_str: the raw text for the Chemkin-formatted file
        :rtype: str
    """

    total_str = ''
    if elem_tuple:
        print("'elem_tuple' input in ckin_io.writer will soon be deprecated!")
    if mech_spc_dct:
        elem_str = elements_block(mech_spc_dct)
        spc_str = species_block(mech_spc_dct)
        total_str += elem_str + spc_str
    if spc_nasa7_dct:
        thermo_str = thermo_block(spc_nasa7_dct)
        total_str += thermo_str
    if rxn_param_dct:
        rxn_str = reactions_block(rxn_param_dct, rxn_cmts_dct=rxn_cmts_dct)
        total_str += rxn_str

    return total_str


def elements_block(mech_spc_dct):
    """ Writes the elements block of the mechanism file

        :param elem_tuple: tuple containing the element names
        :type elem_tuple: tuple
        :return elem_str: str containing the elements block
        :rtype: str
    """

    elem_str = 'ELEMENTS\n\n'
    elem_str += spc.write_elements(mech_spc_dct)
    elem_str += '\nEND\n\n\n'

    return elem_str


def species_block(mech_spc_dct):
    """ Writes the species block of the mechanism file

        :param mech_spc_dct: species data for a mechanism
        :type mech_spc_dct: dct {spc_name:data}
        :return spc_str: str containing the species block
        :rtype: str
    """

    spc_str = 'SPECIES\n\n'
    spc_str += spc.write_species(mech_spc_dct) 
    spc_str += '\nEND\n\n\n'

    return spc_str


def species_block_old(mech_spc_dct):
    """ Writes the species block of the mechanism file

        :param mech_spc_dct: species data for a mechanism
        :type mech_spc_dct: dct {spc_name:data}
        :return spc_str: str containing the species block
        :rtype: str
    """

    # Get the max species name length
    max_spc_len = 0
    for spc in mech_spc_dct.keys():
        if len(spc) > max_spc_len:
            max_spc_len = len(spc)

    # Get the max SMILES name length
    max_smiles_len = 0
    for spc, ident_dct in mech_spc_dct.items():
        if len(ident_dct['smiles']) > max_smiles_len:
            max_smiles_len = len(ident_dct['smiles'])

    buffer = 5

    # Write the spc_str
    spc_str = 'SPECIES\n\n'
    for spc, ident_dct in mech_spc_dct.items():
        spc_str += (
            '{0:<'+str(max_spc_len+buffer)+'s}{1:>9s}{2:<' +
            str(max_smiles_len+buffer)+'s}{3:>9s}{4:<9s}\n').format(
                spc, '! SMILES: ',
                ident_dct['smiles'], 'InChi: ', ident_dct['inchi'])

    spc_str += '\nEND\n\n\n'

    return spc_str


def thermo_block(spc_nasa7_dct):
    """ Writes the thermo block of the mechanism file

    """

    thermo_str = 'THERMO\n'
    thermo_str += '200.00    1000.00   5000.000\n\n'
    for spc_name, params in spc_nasa7_dct.items():
        thermo_str += thermo.thermo_entry(spc_name, params)

    thermo_str += '\nEND\n\n\n'

    return thermo_str


def reactions_block(rxn_param_dct, rxn_cmts_dct=None):
    """ Writes the reaction block of the mechanism file, with optional comments

        :param rxn_param_dct: dct containing the reaction parameters
        :type rxn_param_dct: dct {rxn: params}
        :param rxn_cmts_dct: comment information for each reaction; may also
            include a comment for the entire reactions block
        :type rxn_cmts_dct: dict {rxn: cmts_dct}
        :return total_rxn_str: str containing the reaction block
        :rtype: str
    """

    # Get the overall reactions block comment, if it exists
    if rxn_cmts_dct is not None:
        block_cmt = rxn_cmts_dct.get('block')
        if block_cmt is None:  # if not in the rxn_cmts_dct, set to empty str
            block_cmt = ''
    else:
        block_cmt = ''

    # Write the reactions block
    rxn_str = 'REACTIONS     CAL/MOLE     MOLES\n\n'
    rxn_str += block_cmt
    rxn_str += reaction.write_rxn_param_dct(
        rxn_param_dct, rxn_cmts_dct=rxn_cmts_dct)
    rxn_str += '\n\nEND\n\n'

    return rxn_str
