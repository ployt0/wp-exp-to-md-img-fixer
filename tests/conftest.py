import pytest
import pathlib
from unittest.mock import patch, sentinel, Mock, mock_open, call
import os




@pytest.fixture
def sample_md():
    return """
Lorem ipsum dolor sit amet, consectetur adipiscing elit.:

![Maecenas at tincidunt nibh.](https://mysite.co.uk/wp-content/uploads/210923-24_status.alerting.webp)

Fusce condimentum odio quis molestie mattis.

![Duis ultricies nisl nibh.](https://mysite.co.uk/wp-content/uploads/giblets-bacon.webp)

Praesent congue massa pretium augue condimentum lacinia.

![Suspendisse a nisi sit amet odio.](https://mysite.co.uk/wp-content/uploads/variety-effigies-400x241.webp)

Etiam sed tristique nulla.
"""


@pytest.fixture
def sample_md_2():
    return """
Talking of https://mysite.co.uk/wp-content/uploads/ I'm totally not using image links whilst doing so.

https://mysite.co.uk/wp-content/uploads/ is great. Please see (https://mysite.co.uk/wp-content/uploads/barrel-of-fish.webp).

What about actual, non-image, [links](https://mysite.co.uk/wp-content/uploads/download-this.png)?

Lorem ipsum dolor sit amet, consectetur adipiscing elit.:

![Maecenas at tincidunt nibh.](https://mysite.co.uk/wp-content/uploads/210923-24_status.alerting.webp)

Fusce condimentum odio quis molestie mattis.

![Duis ultricies nisl nibh.](https://mysite.co.uk/wp-content/uploads/giblets-bacon.webp)

Praesent congue massa pretium augue condimentum lacinia.

![Suspendisse a nisi sit amet odio.](https://mysite.co.uk/wp-content/uploads/variety-effigies-400x241.webp)

Etiam sed tristique nulla.
"""


@pytest.fixture
def expected_md_2():
    return """
Talking of https://mysite.co.uk/wp-content/uploads/ I'm totally not using image links whilst doing so.

https://mysite.co.uk/wp-content/uploads/ is great. Please see (https://mysite.co.uk/wp-content/uploads/barrel-of-fish.webp).

What about actual, non-image, [links](https://mysite.co.uk/wp-content/uploads/download-this.png)?

Lorem ipsum dolor sit amet, consectetur adipiscing elit.:

![Maecenas at tincidunt nibh.](images/210923-24_status.alerting.webp)

Fusce condimentum odio quis molestie mattis.

![Duis ultricies nisl nibh.](images/giblets-bacon.webp)

Praesent congue massa pretium augue condimentum lacinia.

![Suspendisse a nisi sit amet odio.](images/variety-effigies-400x241.webp)

Etiam sed tristique nulla.
"""


@pytest.fixture
def stock_args():
    return {
        "old_domain": "http://a/b/c",
        "new_domain": "images/",
        "markdown_source_dir": "app/pages",
        "destination_subdir": "relinked_pages",
        "config_json": None,
        "verbosity": 0,
        "insecure": False,
    }


class Helpers:
    @staticmethod
    def get_path_obj_for_main(path_obj, margs):
        path_obj.rglob = Mock(autospec=True, return_value=[
            pathlib.Path(margs.markdown_source_dir + "/file1.md")])
        return path_obj

    @staticmethod
    def assert_main_file_io(mocked_open, mrglob_rv, expected_md, output_dir):
        expected_calls = [
            call(mrglob_rv[0], "r", encoding="utf-8"),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None),
            call(os.path.join(output_dir, mrglob_rv[0].name), "w",
                 encoding="utf-8"),
            call().__enter__(),
            call().write(expected_md),
            call().__exit__(None, None, None),
        ]
        assert mocked_open.mock_calls == expected_calls


@pytest.fixture
def helpers():
    return Helpers