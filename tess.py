import subprocess
import uuid
import os
import shlex
import argparse
import tempfile

maxproc = 8
debug = False
conv = ('convert -density 300 {doc} -depth 8 '
        '-strip -background white -alpha off {tempfile}')

# tess = ('tesseract {infile} -l {lang} '
#         '-c preserve_interword_spaces=1 {outfile}')
tess = ('tesseract {infile} {outfile} -l {lang}')

def poll_and_popitem(running_ps):
    # Find a terminted process, using temporary output filenames as ids.
    # This is a slow linear search, but that's probably OK since these will
    # be heavily IO-bound processes.
    pop_id = None
    for pid, ps in running_ps.items():
        if ps.poll() is not None:
            pop_id = pid
            break

    # If no process has terminated, pick one at random & remember filename.
    if pop_id is None:
        pop_id, ps = running_ps.popitem()
    else:
        ps = running_ps.pop(pop_id)

    return pop_id, ps

def wait_for_ps(running_ps, infiles, outfiles):
    outfile, ps = poll_and_popitem(running_ps)
    inf = infiles[outfile]
    if ps.wait() == 0:
        outfiles[inf] = outfile
        msg = 'File\n\t{}\nconverted to\n\t{}\nusing `{}`'
        msg = msg.format(inf, outfile, ps.args[0])
    else:
        msg = 'Error: `{}` failed for file\n\t{}'
        msg = msg.format(ps.args[0], inf)
    print(msg)
    print()

def convert_files(files, tempdir):  # instead of tempdir, make_outfile
    running_ps = {}
    docfiles = {}
    outfiles = {}
    for doc in files:
        tempfile = ''  # make_outfile
        while not tempfile or os.path.exists(tempfile):
            tempname = str(uuid.uuid4()) + '.tiff'
            tempfile = os.path.join(tempdir, tempname)

        docfiles[tempfile] = doc
        args = shlex.split(conv.format(doc=doc, tempfile=tempfile))
        print(args)
        ps = subprocess.Popen(args)
        running_ps[tempfile] = ps

        if len(running_ps) > maxproc:
            wait_for_ps(running_ps, docfiles, outfiles)

    while running_ps:
        wait_for_ps(running_ps, docfiles, outfiles)

    return outfiles

def tess_files(infiles, language):  # add make_outfile
    running_ps = {}
    stepfiles = {}
    outfiles = {}
    for infile, stepfile in infiles.items():
        outfile, ext = os.path.splitext(infile)  # make_outfile

        stepfiles[outfile] = stepfile
        args = shlex.split(tess.format(infile=stepfile,
                                       lang=language,
                                       outfile=outfile))
        print(args)
        ps = subprocess.Popen(args)
        running_ps[outfile] = ps

        if len(running_ps) > maxproc:
            wait_for_ps(running_ps, stepfiles, outfiles)

    while running_ps:
        wait_for_ps(running_ps, stepfiles, outfiles)

    return outfiles


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='OCR workflow for a range of file types.'
    )
    parser.add_argument(
        '--language', '-l', default='eng',
        help='The tesseract language ID code for the language you would '
             'like to use. Default is `eng` (English).'
    )
    parser.add_argument(
        'files', nargs='+',
        help='One or more image files to process.'
    )

    args = parser.parse_args()
    files = args.files

    try:
        with tempfile.TemporaryDirectory() as tempdir:
            outfiles = convert_files(files, tempdir)
            outfiles = tess_files(outfiles, args.language)
    except OSError as exc:
        print('Either the `convert` or the `tesseract` command could not '
              'be found.')
        print()
        print('Make sure that you have installed both ImageMagick and '
              'Tesseract, and')
        print('that the `convert` and `tesseract` executables are on the '
              'system path.')
        print()
        print('Here is the original exception message:')
        print()
        print(exc)
        print()
