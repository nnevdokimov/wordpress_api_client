# Wordpress API Client

A Python client for interacting with the WordPress REST API (Posts). This library simplifies common operations such as creating, updating, retrieving, deleting, and listing posts. It is built on top of the `requests` library and integrates logging with `trackrace` (or falls back to Python’s built-in logging).

## Overview

The **Wordpress API Client** provides an easy-to-use interface for working with WordPress posts via the REST API. It supports all the fields and parameters defined in the [WordPress REST API Documentation for Posts](https://developer.wordpress.org/rest-api/reference/posts/), making it a robust solution for developers who need to integrate WordPress functionalities into their Python applications.

### Key Features

- **Create, Update, Delete, and Retrieve Posts:** Manage posts with a simple API.
- **Filtering and Querying:** Use various parameters (e.g., date, author, categories, tags) to filter and search posts.
- **Authentication:** Supports basic authentication using Base64 encoding.
- **Logging:** Integrated logging via `trackrace` (or standard logging as a fallback) for debugging and monitoring API calls.
- **Comprehensive Field Support:** Explicitly supports all fields outlined in the official WordPress REST API documentation.

## Installation

Install the package using pip:

```bash
pip install wordpress-api-client
```

## Usage

Below is a quick example demonstrating how to use the client:

```python
from wordpress_api_client import WordpressClient

# Initialize the client with your WordPress site URL, username, and password.
wp = WordpressClient("https://example.com", "your_username", "your_password")

# Create a new post.
new_post = wp.create_post(
    title="My First Post",
    content="Hello, WordPress!",
    status="publish"
)
print("Created Post ID:", new_post.get("id"))

# Retrieve the created post.
post = wp.get_post(new_post.get("id"))
print("Post Title:", post.get("title", {}).get("rendered"))

# Update the post.
updated_post = wp.update_post(new_post.get("id"), title="Updated Post Title")
print("Updated Post Title:", updated_post.get("title", {}).get("rendered"))

# Delete the post.
deleted_response = wp.delete_post(new_post.get("id"))
print("Deleted Post Response:", deleted_response)

# List posts with filtering (e.g., only 5 posts sorted by date in descending order).
posts_list = wp.list_posts(per_page=5, order="desc", orderby="date")
print("Posts List:", posts_list)
```

## API Reference

For a complete list of parameters and details on how to use each endpoint, please refer to the [WordPress REST API Documentation for Posts](https://developer.wordpress.org/rest-api/reference/posts/).

## Testing

The library includes a set of tests using Python's `unittest` framework. To run the tests, execute:

```bash
python -m unittest discover tests
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on [GitHub](https://github.com/nnevdokimov/wordpress_api_client).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue on the GitHub repository or contact [nick.evdokimovv@gmail.com](mailto:nick.evdokimovv@gmail.com).