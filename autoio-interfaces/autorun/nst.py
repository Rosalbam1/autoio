""" Run NST
"""

import os
import copy
import nst_io
import elstruct
from autorun._run import from_input_string
from autorun._script import SCRIPT_DCT


INPUT_NAME = 'input.dat'
OUTPUT_NAMES = ('output.dat',
                'ne_lz.dat', 'nej_lz.dat',
                'ne_wc.dat', 'nej_wc.dat',
                'hess.1', 'hess.2')


# Specialized runner
def isc_flux(run_dir, prog, geo, charge, mults,
             method, basis, orb_label, ini_kwargs):
    """ Calculate the intersystem crossing flux via a series of calculation
    """

    # Calculate zero energies?
    zero_ene = 0.0

    # Locate geometry at the minimum of the crossing seam
    print('Finding the MSX geometry...')
    msx_geo = msx_geometry(
        run_dir,
        prog, geo, charge, mults, zero_ene,
        method, basis, orb_label, ini_kwargs)

    rot_geo, flux_str = None, None
    if msx_geo is not None:
        # Rotate the msx geometry to the frame for Hessian calculations
        print('Rotating the MSX geometry...')
        rot_geo = rotated_geometry(
            run_dir, prog, msx_geo, zero_ene)

        # Calculate Hessians for msx geometry for both spin states
        print('Calculating Hessians...')
        hessians = hessians_for_nst(
            run_dir,
            prog, rot_geo, charge, mults,
            method, basis, orb_label, ini_kwargs)

        # Use Hessians to calculate intersystem crossing flux
        if hessians is not None:
            print('Calculating Flux...')
            flux_str = isc_flux_from_hessians(
                run_dir, hessians,
                prog, rot_geo, charge, mults, zero_ene,
                method, basis, orb_label, ini_kwargs)

    return rot_geo, hessians, flux_str


def msx_geometry(run_dir,
                 prog, geo, charge, mults, zero_ene,
                 method, basis, orb_label, ini_kwargs):
    """ Obtain the optimized geometry of the MSX
    """

    job_type = 'OPTGM'
    _run_dir = os.path.join(run_dir, 'OPT')

    aux_dct = {
        'qc.1': _qc_input_str('grad', prog, 'GEOMETRY', charge, mults[0],
                              method, basis, orb_label, ini_kwargs[0]),
        'qc.2': _qc_input_str('grad', prog, 'GEOMETRY', charge, mults[1],
                              method, basis, orb_label, ini_kwargs[1]),
        'qc.x': _qc_script_str(prog)
    }

    output_strs = direct(
        _run_dir, job_type,
        prog, geo, zero_ene,
        aux_dct=aux_dct,
        output_names=('output.dat',))

    return nst_io.reader.optimized_msx_geometry(output_strs[0])


def rotated_geometry(run_dir, prog, msx_geo, zero_ene):
    """ Rotate the geometry to the frame
    """

    _run_dir = os.path.join(run_dir, 'ROT')

    output_strs = direct(
        _run_dir, 'ROTGM',
        prog, msx_geo, zero_ene,
        output_names=('output.dat',))

    return nst_io.reader.rotated_geometry(output_strs[0])


def isc_flux_from_hessians(run_dir, hessians,
                           prog, geo, charge, mults, zero_ene,
                           method, basis, orb_label, ini_kwargs):
    """ Determine the isc flux from reading Hessians
    """

    _run_dir = os.path.join(run_dir, 'FLUX')

    aux_dct = {
        'qc.1': _qc_input_str('grad', prog, 'GEOMETRY', charge, mults[0],
                              method, basis, orb_label, ini_kwargs[0]),
        'qc.2': _qc_input_str('grad', prog, 'GEOMETRY', charge, mults[1],
                              method, basis, orb_label, ini_kwargs[1]),
        'qc.x': _qc_script_str(prog),
        'hess.1': nst_io.writer.cartesian_hessian_file(hessians[0]),
        'hess.2': nst_io.writer.cartesian_hessian_file(hessians[1]),
    }

    output_strs = direct(
        _run_dir, 'HESSR',
        prog, geo, zero_ene,
        aux_dct=aux_dct,
        output_names=('ne_lz.dat', 'nej_lz.dat'))

    return output_strs[0]  # grab J-averaged file


def hessians_for_nst(run_dir,
                     prog, geo, charge, mults,
                     method, basis, orb_label, ini_kwargs):
    """ Calculate the two spin state hessians using elstruct
    """

    qc_script_str = _qc_script_str(prog, replace=False)

    hessians = ()
    for idx, mult in enumerate(mults):
        _run_dir = os.path.join(run_dir, 'HESS-{}'.format(idx+1))

        inp_str = _qc_input_str('hess', prog, geo, charge, mult,
                                method, basis, orb_label, ini_kwargs[idx])

        output_strs = from_input_string(qc_script_str, _run_dir, inp_str)
        hessians += (elstruct.reader.hessian(prog, output_strs[0]),)

    if any(hess is None for hess in hessians):
        hessians = None

    return hessians


# General runners
def direct(run_dir, nst_job,
           qc_prog, geo, zero_ene,
           aux_dct=None,
           input_name=INPUT_NAME,
           output_names=OUTPUT_NAMES):
    """ Write input and run output.
    """

    # Write the NST input file and submission file strings
    inp_str = nst_io.writer.input_file(nst_job, geo, zero_ene)
    nst_script_str = _nst_script_str(qc_prog)

    return from_input_string(
        nst_script_str, run_dir, inp_str,
        aux_dct=aux_dct,
        input_name=input_name,
        output_names=output_names)


# Quantum Chemistry input file strings
def _qc_input_str(job, prog, geo, charge, mult,
                  method, basis, orb_lbl, ini_kwargs):
    """ Figure out what the executables and elstruct should be based
        on the desired thy info.
    """

    prog = prog.replace('_mppx', '')
    if prog == 'molpro2015':
        if 'f12' in method:
            ene_line = 'molpro_energy=energy(2)\nshow[1,e25.15],molpro_energy'
        else:
            ene_line = 'molpro_energy=energy\nshow[1,e25.15],molpro_energy'
        _req_gen_lines = {
            2: (
                'nn(1)=1',
                'nn(2)=2',
                'nn(3)=3'
            ),
            3: (
                ene_line,
                '',
                '{force,varsav}'
                '',
                'text,MOLGRAD',
                'table,nn,gradx,grady,gradz',
                'ftyp,f,d,d,d',
            )
        }

        # Add gen lines from input cas kwargs (could have template)
        # to the gen lines set above required for NST to parse qc output
        _nst_gen_lines = ini_kwargs.get('gen_lines', {})
        _nst_gen_lines.update(_req_gen_lines)

        _nst_kwargs = copy.deepcopy(ini_kwargs)
        _nst_kwargs.update({
            'gen_lines': _nst_gen_lines,
        })
        _writer = (elstruct.writer.energy
                   if job == 'grad' else elstruct.writer.hessian)
    else:
        _nst_gen_lines = ini_kwargs.get('gen_lines', {})
        _nst_gen_lines_1 = _nst_gen_lines.get(1, ())
        _nst_gen_lines_1 += ('# fchk NoSym guess=mix',)

        _nst_kwargs = copy.deepcopy(ini_kwargs)
        _nst_kwargs.update({
            'gen_lines': {1: _nst_gen_lines_1}
        })
        _writer = (elstruct.writer.gradient
                   if job == 'grad' else elstruct.writer.hessian)

    # Set the memory and modified orbital restriction label
    _nst_kwargs.update({
        'memory': 10,
        'orb_type': elstruct.util.set_orbital_restriction_label(orb_lbl, mult)
    })

    return _writer(prog, geo, charge, mult, method, basis, **_nst_kwargs)


# Script Submission Strings
def _qc_script_str(prog, replace=True):
    """ Generate the quantum chemistry script string
    """

    script_str = SCRIPT_DCT[prog]
    if replace:
        script_str = script_str.replace('run.inp', 'qc.in')
        script_str = script_str.replace('run.out', 'qc.out')

    return script_str


def _nst_script_str(prog):
    """ Set the NST executable name using the program name in thy info.
    """

    if 'gaussian' in prog:
        exe = "/lcrc/project/CMRP/amech/NST/build/nst-gaussian.x"
    else:
        exe = "/lcrc/project/CMRP/amech/NST/build/nst-molpro.x"
    nst_script_str = (
        "#!/usr/bin/env bash\n"
        "ulimit -c 0\n"
        "{} < input.dat >& output.dat"
    ).format(exe)

    return nst_script_str
