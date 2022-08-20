#!/usr/bin/env python3
"""
The output from https://github.com/lonekorean/wordpress-export-to-markdown
misses some images. The rest are relinked to either a common images folder or
one per post. Assuming the former, this script relinks (fixes) the output from
lonekorean's.
"""
import ssl
from argparse import ArgumentError
import sys
import pathlib
import os
import re
import argparse
import urllib.request
from typing import Optional
from urllib.parse import urlparse
import json

OUTPUT_COLS = 80
COLOUR_YEL = "\033[0;33m"
COLOUR_STOP = "\033[0m"
# These ANSI escape sequences are supported in Windows after:
os.system('color')

class MDImgLinkFinder:
    def __init__(self, former_path):
        self.former_path = former_path
        self.text = None
        self.i = 0

    @staticmethod
    def print_img_link(text, i) -> None:
        start_i = text.rfind("![", 0, i)
        end_i = text.find(")", start_i)
        print(text[start_i:end_i + 1])

    def get_hyperlink(self) -> str:
        end_i = self.text.find(")", self.i)
        return self.text[self.i:end_i]

    def simple_detection(self, md_file) -> None:
        self.i = self.text.find("](" + self.former_path, self.i)
        if self.i > -1:
            start_i = self.text.rfind("![", 0, self.i)
            print(f"{md_file}@{start_i}:")
            MDImgLinkFinder.print_img_link(self.text, self.i)
            self.i += 2


def ensure_wp_uploads_in(former_path):
    if "/wp-content/uploads" not in former_path:
        if not former_path.endswith("/"):
            former_path += "/"
        if former_path.endswith("/wp-content/"):
            former_path += "uploads"
        else:
            former_path += "wp-content/uploads"
    return former_path


def remove_trailing_slash(former_path):
    if former_path.endswith("/"):
        former_path = former_path[:-1]
    return former_path


def parse_args(args_list):
    parser = argparse.ArgumentParser(
        description="Convert image links, in markdown, from an old domain to \"images/\".")
    parser.add_argument(
        "old_domain",
        help="the path, or domain (including http(s)://), that image links "
             "should be converted from. If http, then /wp-content/uploads will"
             "be injected if not already.")
    parser.add_argument(
        "-n", "--new_domain", default="images/",
        help="This will replace the old domain in image links. Should end in a "
             "slash, probably.")
    parser.add_argument(
        "-m", "--markdown_source_dir", default="app/pages",
        help="the source directory containing the markdown files for conversion.")
    parser.add_argument(
        "-d", "--destination_subdir", default="relinked_pages",
        help="the destination subdirectory, adjacent to the source directory. "
        "Converted markdown files go here.")
    parser.add_argument(
        "-c", "--config_json", default=None,
        help="Path to some json to be used in place of command line arguments.")
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0,
        help="increase output verbosity")
    parser.add_argument(
        "-s", "--insecure", action="store_true",
        help="Do NOT verify certificates over https.")
    args = parser.parse_args(args_list)
    if args.config_json is not None:
        with open(args.config_json) as f:
            d = json.load(f)
            for k,v in d.items():
                setattr(args, k, v)
    return args


def get_path_to_pages(pages_dir_path):
    """
    Iterates from the root of the dir path provided until we find a the
    remaining path to be a valid directory in the current working directory.

    Returns the RHS of the path that is below us.
    """
    while pages_dir_path:
        if os.path.isdir(pages_dir_path):
            return pages_dir_path
        pages_dir_path = "/".join(pages_dir_path.split("/")[1:])
    raise FileNotFoundError(
        f"Needs to be run from a directory containing \"{pages_dir_path}\" or "
        "at least a subdirectory on that path.")


def check_if_scaled_and_dl(img_url: str, dest_imgs_dir: str, keep_resizes) ->\
        Optional[str]:
    """
    Downloads the full size image even if a shrunken version was identified.
    The identifier is not updated here so we have keep_resizes as an option
    to continue to download the shrunken version additionally.

    Returns the name of the full sized counterpart if it was found, else None.
    """
    full_img_name = None
    img_name = img_url.split("/")[-1]
    potential_dims = pathlib.Path(img_name).stem.split("-")[-1].split("x")
    if len(potential_dims) == 2 and all(x.isdigit() for x in potential_dims):
        full_img_url = "-".join(img_url.split("-")[:-1]) + "." + img_url.split(".")[-1]
        full_img_name = full_img_url.split("/")[-1]
        try:
            urllib.request.urlretrieve(
                full_img_url, os.path.join(dest_imgs_dir, full_img_name))
        except urllib.error.HTTPError as http404:
            pass
        else:
            print("{}Full sized version of downscaled {} x {} was scraped.{}".format(
                COLOUR_YEL, potential_dims[0], potential_dims[1], COLOUR_STOP))
            if not keep_resizes:
                return full_img_name
    urllib.request.urlretrieve(
        img_url, os.path.join(dest_imgs_dir, img_name))
    return full_img_name


def main(args_list):
    a = parse_args(args_list)
    # Special exception for imgbb.
    if a.old_domain.startswith("http") and not a.old_domain.startswith("https://i.ibb.co"):
        a.old_domain = ensure_wp_uploads_in(a.old_domain)
        a.old_domain = remove_trailing_slash(a.old_domain)
    IMAGE_RE_IN_MD_OUTPUT = fr"(!\[[^]]*]\(){a.old_domain}[^)]*\/([^)]+)\)"
    IMAGE_RE_PATTERN = re.compile(IMAGE_RE_IN_MD_OUTPUT)
    src_pages_dir = get_path_to_pages(a.markdown_source_dir)
    dest_pages_dir = "/".join(src_pages_dir.split("/")[:-1] + [a.destination_subdir])
    pathlib.Path(dest_pages_dir).mkdir(exist_ok=True)
    dest_imgs_dir = "/".join(src_pages_dir.split("/")[:-1] + [a.destination_subdir, a.new_domain])
    pathlib.Path(dest_imgs_dir).mkdir(exist_ok=True)
    print(f"\nGrepping for \"{a.old_domain}\" in {src_pages_dir} to update in {dest_pages_dir}\n")
    img_link_finder = MDImgLinkFinder(a.old_domain)
    # Detect local host/private network and disable secure certification.
    if a.insecure:
        ssl._create_default_https_context = ssl._create_unverified_context

    for md_file in pathlib.Path(src_pages_dir).rglob('*.md'):
        if a.verbosity > 1:
            print(f"Scanning {md_file}")
        with open(md_file, "r", encoding="utf-8") as input_file:
            img_link_finder.text = input_file.read()
        modded_text = IMAGE_RE_PATTERN.sub(
            r"\1" + a.new_domain + r"\2" + ")", img_link_finder.text)

        if img_link_finder.text != modded_text:
            img_link_finder.i = 0
            print("-" * OUTPUT_COLS + "\n")
            while True:
                img_link_finder.simple_detection(md_file)
                if img_link_finder.i == -1:
                    break
                full_img_name = check_if_scaled_and_dl(
                    img_link_finder.get_hyperlink(), dest_imgs_dir, True)
                # todo replace old img_name with full_img_name if not None
                # or make that an option.
                if a.verbosity > 0:
                    print("After SUB".center(OUTPUT_COLS, "-"))
                    img_link_finder.print_img_link(modded_text, img_link_finder.i)
            print("-" * OUTPUT_COLS + "\n")

            with open(os.path.join(dest_pages_dir, md_file.name), "w", encoding="utf-8") as f:
                f.write(modded_text)
            if a.verbosity > 1:
                print(f"Saved modified {md_file.name} to {os.path.join(dest_pages_dir, md_file.name)}")



# For pycharm debugging, only
if __name__ == "__main__":
    main(sys.argv[1:])