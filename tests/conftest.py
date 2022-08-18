import pytest


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