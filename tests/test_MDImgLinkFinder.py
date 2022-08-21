from unittest.mock import patch, sentinel, Mock, mock_open, call

import pytest

from converted_md_corrector import MDImgLinkFinder

def test_init():
    img_link_finder = MDImgLinkFinder("any.old_domain")
    assert img_link_finder.former_path == "any.old_domain"
    assert img_link_finder.i == 0
    assert img_link_finder.text is None


@patch('converted_md_corrector.MDImgLinkFinder.print_img_link')
@patch('builtins.print')
def test_simple_detection(mock_print, mock_print_img_link, sample_md):
    img_link_finder = MDImgLinkFinder("https://mysite.co.uk/wp-content/uploads")
    img_link_finder.text = sample_md
    img_link_finder.simple_detection("print_me")
    assert img_link_finder.i == 91
    assert sample_md.find(img_link_finder.former_path) == 91
    mock_print.assert_called_once_with("print_me@60:")
    mock_print_img_link.assert_called_once_with(sample_md, img_link_finder.i - 2)


@patch('converted_md_corrector.MDImgLinkFinder.print_img_link')
@patch('builtins.print')
def test_simple_detection_of_second(mock_print, mock_print_img_link, sample_md):
    img_link_finder = MDImgLinkFinder("https://mysite.co.uk/wp-content/uploads")
    img_link_finder.text = sample_md
    img_link_finder.i = 91
    img_link_finder.simple_detection("print_me")
    assert img_link_finder.i == 239
    assert sample_md.find(img_link_finder.former_path, 92) == 239
    mock_print.assert_called_once_with("print_me@210:")
    mock_print_img_link.assert_called_once_with(sample_md, img_link_finder.i - 2)


@patch('converted_md_corrector.MDImgLinkFinder.print_img_link')
@patch('builtins.print')
def test_simple_detection_of_third(mock_print, mock_print_img_link, sample_md):
    img_link_finder = MDImgLinkFinder("https://mysite.co.uk/wp-content/uploads")
    img_link_finder.text = sample_md
    img_link_finder.i = 239
    img_link_finder.simple_detection("print_me")
    assert img_link_finder.i == 395
    assert sample_md.find(img_link_finder.former_path, 240) == 395
    mock_print.assert_called_once_with("print_me@358:")
    mock_print_img_link.assert_called_once_with(sample_md, img_link_finder.i - 2)


@patch('converted_md_corrector.MDImgLinkFinder.print_img_link')
@patch('builtins.print')
def test_simple_detection_using_just_domain(mock_print, mock_print_img_link, sample_md):
    img_link_finder = MDImgLinkFinder("https://mysite.co.uk")
    img_link_finder.text = sample_md
    img_link_finder.simple_detection("print_me")
    assert img_link_finder.i == 91
    assert sample_md.find(img_link_finder.former_path) == 91
    mock_print.assert_called_once_with("print_me@60:")
    mock_print_img_link.assert_called_once_with(sample_md, img_link_finder.i - 2)


@patch('converted_md_corrector.MDImgLinkFinder.print_img_link')
@patch('builtins.print')
def test_simple_detection_relinking_old_folder(mock_print, mock_print_img_link):
    img_link_finder = MDImgLinkFinder("relpath_to_imgs")
    locally_linked_md = """
Lorem ipsum dolor sit amet.:

![Maecenas at tincidunt nibh.](relpath_to_imgs/210923-24_status.alerting.webp)

Fusce condimentum odio quis molestie mattis.
    """

    img_link_finder.text = locally_linked_md
    img_link_finder.simple_detection("print_me")
    assert img_link_finder.i == 62
    assert locally_linked_md.find(img_link_finder.former_path) == 62
    mock_print.assert_called_once_with("print_me@31:")
    mock_print_img_link.assert_called_once_with(locally_linked_md, img_link_finder.i - 2)


@patch('converted_md_corrector.MDImgLinkFinder.print_img_link')
@patch('builtins.print')
def test_simple_detection_atypical_img_md(mock_print, mock_print_img_link):
    img_link_finder = MDImgLinkFinder("relpath_to_imgs")
    # I sometimes do this to reduce my column count, I find most interpreters
    # accept it:
    atypical_md = """
Lorem ipsum dolor sit amet.:

![Maecenas at tincidunt nibh.](
relpath_to_imgs/210923-24_status.alerting.webp)

Fusce condimentum odio quis molestie mattis.
    """
    img_link_finder.text = atypical_md
    img_link_finder.simple_detection("print_me")
    assert img_link_finder.i == 62
    assert atypical_md.find(img_link_finder.former_path) == 63
    mock_print.assert_called_once_with("print_me@31:")
    mock_print_img_link.assert_called_once_with(atypical_md, img_link_finder.i - 2)


def test_simple_detection_lookahead_of_redherring():
    img_link_finder = MDImgLinkFinder("something_long_enough_to_overflow")
    atypical_md = """
Lorem ipsum dolor sit amet.:

[this might be a closing link](#link1)"""
    img_link_finder.text = atypical_md
    img_link_finder.simple_detection("print_me")
    # it has to progress, so we don't infinite loop:
    assert img_link_finder.i == 62
    img_link_finder.simple_detection("print_me")
    assert img_link_finder.i == -1


@patch('converted_md_corrector.MDImgLinkFinder.print_img_link')
@patch('builtins.print')
def test_simple_detection_infinite_loop_scenario(mock_print, mock_print_img_link):
    img_link_finder = MDImgLinkFinder("diz")
    atypical_md = """
Lorem ipsum dolor sit amet.:

![Maecenas at tincidunt nibh.](diz/alerting.webp)

![Not this](dat/alerting.webp)"""
    img_link_finder.text = atypical_md
    img_link_finder.simple_detection("print_me")
    mock_print.assert_called_once_with("print_me@31:")
    # it has to progress, so we don't infinite loop:
    assert img_link_finder.i == 62
    mock_print_img_link.assert_called_once_with(atypical_md, 60)

    # Assert nothing was output but we still scanned the non-matching image at
    # the end.
    img_link_finder.simple_detection("print_me")
    mock_print.assert_called_once_with("print_me@31:")
    mock_print_img_link.assert_called_once_with(atypical_md, 60)
    assert img_link_finder.i == 94


@patch('builtins.print')
def test_print_img_link(mock_print, sample_md):
    MDImgLinkFinder.print_img_link(sample_md, 89)
    mock_print.assert_called_once_with(
        "![Maecenas at tincidunt nibh.](https://mysite.co.uk/wp-content/uploads/210923-24_status.alerting.webp)"
    )


@patch('builtins.print')
def test_print_img_link_2(mock_print, sample_md):
    MDImgLinkFinder.print_img_link(sample_md, 237)
    mock_print.assert_called_once_with(
        "![Duis ultricies nisl nibh.](https://mysite.co.uk/wp-content/uploads/giblets-bacon.webp)"
    )


@patch('builtins.print')
def test_print_img_link_3(mock_print, sample_md):
    MDImgLinkFinder.print_img_link(sample_md, 393)
    mock_print.assert_called_once_with(
        "![Suspendisse a nisi sit amet odio.](https://mysite.co.uk/wp-content/uploads/variety-effigies-400x241.webp)"
    )


def test_get_hyperlink(sample_md):
    img_link_finder = MDImgLinkFinder("https://mysite.co.uk/wp-content/uploads")
    img_link_finder.text = sample_md
    img_link_finder.i = 91
    hyper = img_link_finder.get_hyperlink()
    assert hyper == "https://mysite.co.uk/wp-content/uploads/210923-24_status.alerting.webp"


def test_get_hyperlink_using_just_domain(sample_md):
    img_link_finder = MDImgLinkFinder("https://mysite.co.uk")
    img_link_finder.text = sample_md
    img_link_finder.i = 91
    hyper = img_link_finder.get_hyperlink()
    assert hyper == "https://mysite.co.uk/wp-content/uploads/210923-24_status.alerting.webp"


def test_get_hyperlink_to_resized(sample_md):
    img_link_finder = MDImgLinkFinder("https://mysite.co.uk/wp-content/uploads")
    img_link_finder.text = sample_md
    img_link_finder.i = 395
    hyper = img_link_finder.get_hyperlink()
    assert hyper == "https://mysite.co.uk/wp-content/uploads/variety-effigies-400x241.webp"



