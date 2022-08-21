import ssl
from argparse import Namespace
import pathlib
from unittest.mock import patch, sentinel, Mock, mock_open, call

import pytest
import os
import urllib.error

from converted_md_corrector import remove_trailing_slash, parse_args, ensure_wp_uploads_in, get_path_to_pages, check_if_scaled_and_dl, main


def test_parse_args_for_help():
    with pytest.raises(SystemExit):
        parse_args(["-h"])



def test_parse_args_basic():
    MOCK_ARGS_LIST = ["the_old_domain.com"]
    args = parse_args(MOCK_ARGS_LIST)
    assert args.old_domain == MOCK_ARGS_LIST[0]
    assert args.markdown_source_dir == "app/pages"
    assert args.destination_subdir == "relinked_pages"
    assert args.config_json is None
    assert args.verbosity == 0


def test_parse_args():
    MOCK_ARGS_LIST = ["the_old_domain.com", "-m", "src/pages"]
    args = parse_args(MOCK_ARGS_LIST)
    assert args.old_domain == MOCK_ARGS_LIST[0]
    assert args.markdown_source_dir == MOCK_ARGS_LIST[2]
    assert args.destination_subdir == "relinked_pages"
    assert args.config_json is None
    assert args.verbosity == 0


def test_parse_args_from_config():
    MOCK_ARGS_LIST = ["the_old_domain.com", "-m", "src/pages", "-c", "sentinel.location"]
    with patch("builtins.open", mock_open(
        read_data='{"markdown_source_dir":"myownpages","destination_subdir":"fudgestop"}')) as mocked_open:
        args = parse_args(MOCK_ARGS_LIST)

    mocked_open.assert_called_once_with(MOCK_ARGS_LIST[-1])
    assert args.old_domain == MOCK_ARGS_LIST[0]
    assert args.markdown_source_dir == "myownpages"
    assert args.destination_subdir == "fudgestop"
    assert args.config_json == MOCK_ARGS_LIST[-1]
    assert args.verbosity == 0


def test_ensure_wp_uploads_in():
    starting_path = "this/isn't/right"
    fixed_path = ensure_wp_uploads_in(starting_path)
    assert fixed_path == starting_path + "/wp-content/uploads"
    fixed_path = ensure_wp_uploads_in(starting_path + "/")
    assert fixed_path == starting_path + "/wp-content/uploads"
    fixed_path = ensure_wp_uploads_in(starting_path + "/wp-content/uploads")
    assert fixed_path == starting_path + "/wp-content/uploads"
    fixed_path = ensure_wp_uploads_in(starting_path + "/wp-content")
    assert fixed_path == starting_path + "/wp-content/uploads"


def test_remove_trailing_slash():
    assert remove_trailing_slash("ad.a/geh/") == "ad.a/geh"
    assert remove_trailing_slash("/ad.a/geh/") == "/ad.a/geh"
    assert remove_trailing_slash("ad.a/geh") == "ad.a/geh"
    assert remove_trailing_slash("/ad.a/geh") == "/ad.a/geh"


@patch("converted_md_corrector.os.path.isdir", autospec=True, return_value=True)
def test_get_path_to_pages(mock_isdir):
    assert get_path_to_pages(sentinel.dir) == sentinel.dir
    mock_isdir.assert_called_once_with(sentinel.dir)


@patch("converted_md_corrector.os.path.isdir", autospec=True, side_effect=[False, True])
def test_get_path_to_pages_displaced(mock_isdir):
    sample_path = "a/b/c/d/"
    assert get_path_to_pages(sample_path) == "b/c/d/"
    mock_isdir.assert_has_calls([
        call("a/b/c/d/"),
        call("b/c/d/")
    ])


@patch("converted_md_corrector.os.path.isdir", autospec=True, side_effect=[False, False, False, False])
def test_get_path_to_pages2(mock_isdir):
    sample_path = "a/b/c/d/"
    with pytest.raises(FileNotFoundError) as FNFErr:
        get_path_to_pages(sample_path)
    mock_isdir.assert_has_calls([
        call("a/b/c/d/"),
        call("b/c/d/"),
        call("c/d/"),
        call("d/"),
    ])


STOCK_404 = urllib.error.HTTPError("sentinel.404", 404, "testing", None, None)

@pytest.mark.parametrize("img_url,keep_resizes,expected_retrieves,side_effect", [
    # Don't want downscale, and weren't given downscaled URL:
    ("https://g8.co/a/b/c.png", False, [("https://g8.co/a/b/c.png", "c.png")], None),
    # Don't want given downscale, and full size is available:
    ("https://g8.co/a/b/c-24x48.png", False, [("https://g8.co/a/b/c.png", "c.png")], None),
    # Want both, can fetch both:
    ("https://g8.co/a/b/c-24x48.png", True, [
        ("https://g8.co/a/b/c.png", "c.png"), ("https://g8.co/a/b/c-24x48.png", "c-24x48.png")
    ], None),
    # Want both, fetching full size fails:
    ("https://g8.co/a/b/c-24x48.png", True, [
        ("https://g8.co/a/b/c.png", "c.png"), ("https://g8.co/a/b/c-24x48.png", "c-24x48.png")
    ], [STOCK_404, None]),
    # Don't want downscale but take it because full is 404:
    ("https://g8.co/a/b/c-24x48.png", False, [
        ("https://g8.co/a/b/c.png", "c.png"), ("https://g8.co/a/b/c-24x48.png", "c-24x48.png")
    ], [STOCK_404, None]),
])
@patch("converted_md_corrector.urllib.request.urlretrieve", autospec=True)
def test_check_if_scaled_and_dl_paramd(mock_urlretrieve, img_url, keep_resizes, expected_retrieves, side_effect):
    mock_urlretrieve.side_effect = side_effect
    dest_imgs_dir = "sentinel.dir"
    check_if_scaled_and_dl(img_url, dest_imgs_dir, keep_resizes)
    mock_urlretrieve.assert_has_calls([
        call(x[0], os.path.join(dest_imgs_dir, x[1]))
            for x in expected_retrieves
    ])


@patch("converted_md_corrector.check_if_scaled_and_dl", autospec=True)
@patch("converted_md_corrector.pathlib.Path", autospec=True)
@patch("converted_md_corrector.get_path_to_pages", side_effect=lambda x: x)
@patch("converted_md_corrector.parse_args", autospec=True)
def test_main(
        mock_parse_args,
        mock_get_path_to_pages,
        mock_path,
        mock_check_if_scaled_and_dl,
        sample_md, stock_args, helpers):
    mock_parse_args.return_value = Namespace(**(stock_args | {
        "old_domain": "https://mysite.co.uk/wp-content/uploads/",
        "verbosity": 2
    }))
    margs = mock_parse_args.return_value
    path_obj = helpers.get_path_obj_for_main(mock_path.return_value, margs)
    output_dir = "/".join(margs.markdown_source_dir.split("/")[:-1] + [margs.destination_subdir])
    img_op_dir = "/".join(margs.markdown_source_dir.split("/")[:-1] + [margs.destination_subdir, margs.new_domain])
    with patch("builtins.open", mock_open(read_data=sample_md)) as mocked_open:
        main(["https://mysite.co.uk/wp-content/uploads/"])
    expected_md = sample_md.replace("](https://mysite.co.uk/wp-content/uploads/", "](images/")
    helpers.assert_main_file_io(mocked_open, path_obj.rglob.return_value, expected_md, output_dir)
    mock_get_path_to_pages.assert_called_once_with(margs.markdown_source_dir)
    mock_check_if_scaled_and_dl.assert_has_calls([
        call("https://mysite.co.uk/wp-content/uploads/210923-24_status.alerting.webp", img_op_dir, True),
        call("https://mysite.co.uk/wp-content/uploads/giblets-bacon.webp", img_op_dir, True),
        call("https://mysite.co.uk/wp-content/uploads/variety-effigies-400x241.webp", img_op_dir, True),
    ])


@patch("converted_md_corrector.ssl._create_unverified_context", autospec=True)
@patch("converted_md_corrector.check_if_scaled_and_dl", autospec=True)
@patch("converted_md_corrector.pathlib.Path", autospec=True)
@patch("converted_md_corrector.get_path_to_pages", side_effect=lambda x: x)
@patch("converted_md_corrector.parse_args", autospec=True)
def test_main_insecure(
        mock_parse_args,
        mock_get_path_to_pages,
        mock_path,
        mock_check_if_scaled_and_dl,
        mock_mk_unverified_context,
        sample_md, stock_args, helpers):
    mock_parse_args.return_value = Namespace(**(stock_args | {
        "old_domain": "https://mysite.co.uk/wp-content/uploads/",
        "verbosity": 2,
        "insecure": True
    }))
    margs = mock_parse_args.return_value
    path_obj = helpers.get_path_obj_for_main(mock_path.return_value, margs)
    output_dir = "/".join(margs.markdown_source_dir.split("/")[:-1] + [margs.destination_subdir])
    img_op_dir = "/".join(margs.markdown_source_dir.split("/")[:-1] + [margs.destination_subdir, margs.new_domain])
    with patch("builtins.open", mock_open(read_data=sample_md)) as mocked_open:
        main(["https://mysite.co.uk/wp-content/uploads/"])
    expected_md = sample_md.replace("](https://mysite.co.uk/wp-content/uploads/", "](images/")
    helpers.assert_main_file_io(mocked_open, path_obj.rglob.return_value, expected_md, output_dir)
    mock_get_path_to_pages.assert_called_once_with(margs.markdown_source_dir)
    mock_check_if_scaled_and_dl.assert_has_calls([
        call("https://mysite.co.uk/wp-content/uploads/210923-24_status.alerting.webp", img_op_dir, True),
        call("https://mysite.co.uk/wp-content/uploads/giblets-bacon.webp", img_op_dir, True),
        call("https://mysite.co.uk/wp-content/uploads/variety-effigies-400x241.webp", img_op_dir, True),
    ])
    assert ssl._create_default_https_context == mock_mk_unverified_context


@patch("converted_md_corrector.check_if_scaled_and_dl", autospec=True)
@patch("converted_md_corrector.pathlib.Path", autospec=True)
@patch("converted_md_corrector.get_path_to_pages", side_effect=lambda x: x)
@patch("converted_md_corrector.parse_args", autospec=True)
def test_main_harder(
        mock_parse_args,
        mock_get_path_to_pages,
        mock_path,
        mock_check_if_scaled_and_dl,
        sample_md_2, expected_md_2, stock_args, helpers):
    mock_parse_args.return_value = Namespace(**(stock_args | {
        "old_domain": "https://mysite.co.uk/wp-content/uploads/",
    }))
    margs = mock_parse_args.return_value
    path_obj = helpers.get_path_obj_for_main(mock_path.return_value, margs)
    output_dir = "/".join(margs.markdown_source_dir.split("/")[:-1] + [margs.destination_subdir])
    img_op_dir = "/".join(margs.markdown_source_dir.split("/")[:-1] + [margs.destination_subdir, margs.new_domain])
    with patch("builtins.open", mock_open(read_data=sample_md_2)) as mocked_open:
        main(["https://mysite.co.uk/wp-content/uploads/"])
    helpers.assert_main_file_io(mocked_open, path_obj.rglob.return_value, expected_md_2, output_dir)
    mock_get_path_to_pages.assert_called_once_with(margs.markdown_source_dir)
    mock_check_if_scaled_and_dl.assert_has_calls([
        call("https://mysite.co.uk/wp-content/uploads/210923-24_status.alerting.webp", img_op_dir, True),
        call("https://mysite.co.uk/wp-content/uploads/giblets-bacon.webp", img_op_dir, True),
        call("https://mysite.co.uk/wp-content/uploads/variety-effigies-400x241.webp", img_op_dir, True),
    ])


