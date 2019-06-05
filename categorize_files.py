#!/usr/bin/env python3

"""
Create a categorized image of an unorganized directory (e.g. disk dump).
Each contained file is classified according to its suffix or MIME type and
moved/copied/linked to a corresponding directory in the output directory.
"""

import sys
import os
from pathlib import Path
import shutil
import argparse
import mimetypes
import logging

import magic  # https://github.com/ahupp/python-magic


def parse_arguments():
    """ A wrapper around the argparse code. """
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-c', '--criterion', action='store',
                        choices=['suffix', 'mime_name', 'mime_content'],
                        required=True,
                        help="a criterion by which files are classified")
    parser.add_argument('-p', '--operation', action='store',
                        choices=['move', 'copy', 'hard_link', 'symbolic_link'],
                        required=True,
                        help="a file system operation used to create the "
                             "categorized files")
    parser.add_argument('-i', '--image-structure', action='store',
                        choices=['flat_name', 'flat_path', 'nested'],
                        default='flat_name',
                        help="image file/directory structure")

    parser.add_argument('--remove-leading-dots', action='store_true',
                        help="unhide hidden files in Unix and Unix-like "
                             "environments")
    parser.add_argument('--replace-on-collision', action='store_true',
                        help="don't create unique destination file names, "
                             "colliding files will be replaced")
    parser.add_argument('-l', '--log-level', action='store',
                        choices=['debug', 'info', 'warning', 'error',
                                 'critical'], default='warning',
                        help="set a logging level; messages which are less "
                             "severe will be ignored")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="don't actually do anything, just show what "
                             "would be done")

    parser.add_argument('-o', '--output-dir', action='store', type=Path,
                        help="set an output directory for the categorized "
                             "image")
    parser.add_argument('input_dir', type=Path, nargs=1,
                        help="input directory")

    return parser.parse_args()


def get_file_category(file_path: Path) -> str:
    """ Determine the category of the given file. """
    if ARGS.criterion == 'suffix':
        category = file_path.suffix[1:].lower()
    elif ARGS.criterion == 'mime_name':
        category = mimetypes.guess_type(file_path.name)[0]
    elif ARGS.criterion == 'mime_content':
        category = magic.from_file(str(file_path), mime=True)

    # the category can't be determined: missing or unknown suffix
    if not category:
        category = 'unknown'

    return category


def get_dst_file_path(src_file_rel: Path, dst_dir: Path) -> Path:
    """
    Construct a destination file name based on the source file name,
    destination directory, and desired image structure.
    """
    if ARGS.image_structure == 'flat_name':
        # use just the file name, collisions are possible
        dst_file = Path(dst_dir, src_file_rel.name)
    elif ARGS.image_structure == 'flat_path':
        # Replace all path separator characters with underscores. Use
        # as_posix() to get forward slashes on every OS.
        src_file_rel_flat = src_file_rel.as_posix().replace('/', '_')
        dst_file = Path(dst_dir, src_file_rel_flat)
    elif ARGS.image_structure == 'nested':
        # copy the directory hierarchy from the source
        dst_file = Path(dst_dir, src_file_rel)

    # remove all leading dost from the file name, this will unhide hidden files
    # in Unix and Unix-like environments
    if ARGS.remove_leading_dots and dst_file.name[0] == '.':
        dst_file_orig = dst_file
        dst_file = dst_file.with_name(dst_file.name.lstrip('.'))
        logging.info("removing leading dots: `%s' -> `%s'", dst_file_orig,
                     dst_file)

    return dst_file


def src_to_dst_operation(src_file: Path, dst_file: Path):
    """
    Handle collisions, then create the destination file from the source file by
    a move/copy/link operation.
    """
    try:
        # destination name collision handling
        # does not work in the dry run mode
        if dst_file.exists():
            if ARGS.replace_on_collision:
                logging.info("name collision: `%s' will replace `%s'",
                             src_file, dst_file)
                dst_file.unlink()
            else:  # create a unique file name to prevent overwriting
                dst_file_orig = dst_file
                collision_cnt = 1
                while dst_file.exists():
                    dst_file = dst_file.with_name(
                        f"{dst_file_orig.name}.{collision_cnt}")
                    collision_cnt += 1
                logging.info("name collision: `%s' will be saved as `%s'",
                             src_file, dst_file)

        # perform the file system operation
        if ARGS.operation == 'move':
            logging.debug("moving (renaming) `%s' to `%s'", src_file, dst_file)
            if not ARGS.dry_run:
                src_file.rename(dst_file)
        elif ARGS.operation == 'copy':
            logging.debug("copying `%s' to `%s'", src_file, dst_file)
            if not ARGS.dry_run:
                shutil.copyfile(src_file, dst_file)
        elif ARGS.operation == 'hard_link':
            logging.debug("creating a hard link pointing to `%s' named `%s'",
                          src_file, dst_file)
            if not ARGS.dry_run:
                os.link(src_file, dst_file)
        elif ARGS.operation == 'symbolic_link':
            src_file_abs = src_file.resolve()
            logging.debug("creating a symlink pointing to `%s' named `%s'",
                          src_file_abs, dst_file)
            if not ARGS.dry_run:
                dst_file.symlink_to(src_file_abs)
    except OSError as ex:
        logging.warning(ex)


def main():
    """
    Setup input and output directories, then recursively walk the input
    directory, classify each file, and fill the categorized image directory.
    """
    # set the logging level from a command-line option
    logging.basicConfig(level=getattr(logging, ARGS.log_level.upper()))

    # check the input directory
    input_dir = ARGS.input_dir[0]  # positional args are always a list
    if not input_dir.is_dir():
        logging.error("%s: does not exist or is not a directory", input_dir)
        return 1

    # select the output directory
    if ARGS.output_dir:
        output_dir = ARGS.output_dir
    else:
        output_dir = Path(input_dir.name + '_categorized_by_' + ARGS.criterion)

    # ensure that the output directory is not inside the input directory
    try:
        # input directory must exist
        input_dir_abs = input_dir.resolve(strict=True)
        # output directory must not exist
        output_dir_abs = output_dir.resolve(strict=False)
    except (FileNotFoundError, RuntimeError) as ex:
        logging.error(ex)
        return 1
    if input_dir_abs in output_dir_abs.parents:
        logging.error("the output directory is inside the input directory. "
                      "That could create an infinite loop.")
        return 1

    # create the output directory
    if not ARGS.dry_run:
        try:
            output_dir.mkdir()
        except (FileExistsError, FileNotFoundError) as ex:
            logging.error(ex)
            return 1

    logging.info("using input directory `%s'", input_dir)
    logging.info("using output directory `%s'", output_dir)

    # loop through this directory and all subdirectories, recursively
    for src_file in input_dir.rglob('*'):
        if src_file.is_file():  # skip everything but regular files
            src_file_rel = src_file.relative_to(input_dir)

            # classify the file and construct its output path
            category = get_file_category(src_file)
            dst_file = get_dst_file_path(src_file_rel,
                                         Path(output_dir, category))
            # create output directories if needed
            if not ARGS.dry_run:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
            # move/copy/link src to dst
            src_to_dst_operation(src_file, dst_file)

    return 0


if __name__ == '__main__':
    ARGS = parse_arguments()
    sys.exit(main())
