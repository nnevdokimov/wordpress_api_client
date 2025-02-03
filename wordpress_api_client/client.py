import base64
from typing import Any, Dict, Optional, List, Union

import requests

try:
    import trackrace

    logger = trackrace.get_logger(__name__)
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class WordpressClient:
    """
    A library for working with WordPress posts via REST API.

    Supported methods:
      - create_post(...): Creating a new post.
      - get_post(post_id, context=‘view’, password=None): Get post by ID.
      - update_post(post_id, ...): Updating an existing post.
      - delete_post(post_id, force=True): Deleting a post.
      - list_posts(...): Retrieving a list of posts with filters.

    All fields are explicitly specified in the post creation and update methods.
    """

    def __init__(self, base_url: str, login: str, password: str) -> None:
        """
        WordPress client initialisation.

        :param base_url: URL of the site (e.g. ‘https://example.com’)
        :param login: User login with publishing rights
        :param password: User password
        """
        self.base_url = base_url.rstrip('/')
        self.login = login
        self.password = password
        auth_str = f"{self.login}:{self.password}"
        self.headers = {
            'Authorization': 'Basic ' + base64.b64encode(auth_str.encode('utf-8')).decode('utf-8'),
            'Content-Type': 'application/json'
        }
        logger.info("WordpressPoster initialized for base URL: %s", self.base_url)

    @staticmethod
    def _prepare_text_field(field: Optional[Union[str, Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        """
        Converts a text field (title, content, excerpt) to a dictionary format with the ‘rendered’ key.
        If the field is already a dictionary, returns it unchanged.
        """
        if field is None:
            return None
        if isinstance(field, str):
            return {"rendered": field}
        return field

    @staticmethod
    def _format_query_param(value: Any) -> Any:
        """
        If the value is a list, converts it to a comma-separated string.
        This is convenient for passing parameters in GET requests.
        """
        if isinstance(value, list):
            return ",".join(str(x) for x in value)
        return value

    def create_post(
            self,
            post_endpoint: Optional[str] = '',
            date: Optional[str] = None,
            date_gmt: Optional[str] = None,
            slug: Optional[str] = None,
            status: Optional[str] = 'draft',
            password_field: Optional[str] = None,
            title: Optional[Union[str, Dict[str, Any]]] = None,
            content: Optional[Union[str, Dict[str, Any]]] = None,
            author: Optional[int] = None,
            excerpt: Optional[Union[str, Dict[str, Any]]] = None,
            featured_media: Optional[int] = None,
            comment_status: Optional[str] = None,  # 'open' или 'closed'
            ping_status: Optional[str] = None,  # 'open' или 'closed'
            post_format: Optional[str] = None,
            # standard, aside, chat, gallery, link, image, quote, status, video, audio
            meta: Optional[Dict[str, Any]] = None,
            sticky: Optional[bool] = None,
            template: Optional[str] = None,
            categories: Optional[List[int]] = None,
            tags: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Creates a new post.

        :param post_endpoint: Main endpoint of the post (classically is 'post')
        :param date: Publication date in site time zone (ISO8601)
        :param date_gmt: Post date in GMT (ISO8601)
        :param slug: Unique character identifier of the post
        :param status: Status of the post (‘publish’, ‘draft’, ‘pending’, ‘private’, ‘future’)
        :param password_field: Password to protect the post
        :param title: Post title (either string or object { ‘rendered’: ‘...’ })
        :param content: The content of the post (either a string or an object)
        :param author: Post author ID
        :param excerpt: Excerpt (either string or object)
        :param featured_media: ID of image or media object
        :param comment_status: Comment status (‘open’ or ‘closed’)
        :param ping_status: Ping status (‘open’ or ‘closed’)
        :param post_format: Post format (e.g. ‘standard’)
        :param meta: Dictionary of arbitrary meta fields
        :param sticky: Flag of post stickiness
        :param template: Name of the template file to display
        :param categories: List of category IDs
        :param tags: List of tag IDs
        :return: JSON response from server (pending status 201)
        :raises Exception: If post creation failed
        """
        payload: Dict[str, Any] = {}

        if date is not None:
            payload["date"] = date
        if date_gmt is not None:
            payload["date_gmt"] = date_gmt
        if slug is not None:
            payload["slug"] = slug
        if status is not None:
            payload["status"] = status
        if password_field is not None:
            payload["password"] = password_field

        title_prepared = self._prepare_text_field(title)
        if title_prepared is not None:
            payload["title"] = title_prepared

        content_prepared = self._prepare_text_field(content)
        if content_prepared is not None:
            payload["content"] = content_prepared

        if author is not None:
            payload["author"] = author

        excerpt_prepared = self._prepare_text_field(excerpt)
        if excerpt_prepared is not None:
            payload["excerpt"] = excerpt_prepared

        if featured_media is not None:
            payload["featured_media"] = featured_media
        if comment_status is not None:
            payload["comment_status"] = comment_status
        if ping_status is not None:
            payload["ping_status"] = ping_status
        if post_format is not None:
            payload["format"] = post_format
        if meta is not None:
            payload["meta"] = meta
        if sticky is not None:
            payload["sticky"] = sticky
        if template is not None:
            payload["template"] = template
        if categories is not None:
            payload["categories"] = categories
        if tags is not None:
            payload["tags"] = tags

        url = f"{self.base_url}/wp-json/wp/v2/{post_endpoint}"
        logger.info("Creating post with payload: %s", payload)
        response = requests.post(url, headers=self.headers, json=payload)
        logger.debug("Response: %s", response.text)
        if response.status_code != 201:
            logger.error("Failed to create post: %s %s", response.status_code, response.text)
            raise Exception(f"Failed to create post: {response.status_code} {response.text}")
        logger.info("Post created successfully with id %s", response.json().get("id"))
        return response.json()

    def get_post(self, post_id: int, context: str = 'view', password: Optional[str] = None) -> Dict[str, Any]:
        """
        Получает пост по ID.

        :param post_id: Идентификатор поста
        :param context: Контекст запроса ('view', 'embed', 'edit')
        :param password: Пароль для защищённого поста
        :return: JSON-ответ с данными поста
        :raises Exception: Если получение поста не удалось (ожидается статус 200)
        """
        params = {'context': context}
        if password:
            params['password'] = password

        url = f"{self.base_url}/wp-json/wp/v2/posts/{post_id}"
        logger.info("Retrieving post id %s with params: %s", post_id, params)
        response = requests.get(url, headers=self.headers, params=params)
        logger.debug("Response: %s", response.text)
        if response.status_code != 200:
            logger.error("Failed to retrieve post %s: %s %s", post_id, response.status_code, response.text)
            raise Exception(f"Failed to retrieve post {post_id}: {response.status_code} {response.text}")
        logger.info("Post %s retrieved successfully", post_id)
        return response.json()

    def update_post(
            self,
            post_id: int,
            date: Optional[str] = None,
            date_gmt: Optional[str] = None,
            slug: Optional[str] = None,
            status: Optional[str] = None,
            password_field: Optional[str] = None,
            title: Optional[Union[str, Dict[str, Any]]] = None,
            content: Optional[Union[str, Dict[str, Any]]] = None,
            author: Optional[int] = None,
            excerpt: Optional[Union[str, Dict[str, Any]]] = None,
            featured_media: Optional[int] = None,
            comment_status: Optional[str] = None,
            ping_status: Optional[str] = None,
            post_format: Optional[str] = None,
            meta: Optional[Dict[str, Any]] = None,
            sticky: Optional[bool] = None,
            template: Optional[str] = None,
            categories: Optional[List[int]] = None,
            tags: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Updates an existing post in WordPress.

        This method allows updating various attributes of a post, such as its title, content, status, categories,
        tags, and other metadata. The request is sent to the WordPress REST API and requires authentication.

        :param post_id: The unique identifier of the post to be updated.
        :param date: The date when the post was published (ISO8601 format).
        :param date_gmt: The publication date in GMT timezone (ISO8601 format).
        :param slug: The URL-friendly identifier for the post.
        :param status: The status of the post ('publish', 'draft', 'pending', 'private', 'future').
        :param password_field: A password to protect access to the post.
        :param title: The title of the post (either a string or a dictionary with {"rendered": "..."}).
        :param content: The main content of the post (either a string or a dictionary with {"rendered": "..."}).
        :param author: The ID of the author of the post.
        :param excerpt: A short summary of the post (either a string or a dictionary with {"rendered": "..."}).
        :param featured_media: The ID of the featured image/media for the post.
        :param comment_status: Whether comments are open ('open' or 'closed').
        :param ping_status: Whether the post can be pinged ('open' or 'closed').
        :param post_format: The format of the post ('standard', 'aside', 'chat', 'gallery', 'link', 'image',
                            'quote', 'status', 'video', 'audio').
        :param meta: A dictionary of custom meta fields for the post.
        :param sticky: Whether the post should be marked as sticky (True or False).
        :param template: The template file to be used for displaying the post.
        :param categories: A list of category IDs assigned to the post.
        :param tags: A list of tag IDs assigned to the post.
        :return: A JSON response containing the updated post data.
        :raises Exception: If the request fails or returns an error response.
        """
        payload: Dict[str, Any] = {}

        if date is not None:
            payload["date"] = date
        if date_gmt is not None:
            payload["date_gmt"] = date_gmt
        if slug is not None:
            payload["slug"] = slug
        if status is not None:
            payload["status"] = status
        if password_field is not None:
            payload["password"] = password_field

        title_prepared = self._prepare_text_field(title)
        if title_prepared is not None:
            payload["title"] = title_prepared

        content_prepared = self._prepare_text_field(content)
        if content_prepared is not None:
            payload["content"] = content_prepared

        if author is not None:
            payload["author"] = author

        excerpt_prepared = self._prepare_text_field(excerpt)
        if excerpt_prepared is not None:
            payload["excerpt"] = excerpt_prepared

        if featured_media is not None:
            payload["featured_media"] = featured_media
        if comment_status is not None:
            payload["comment_status"] = comment_status
        if ping_status is not None:
            payload["ping_status"] = ping_status
        if post_format is not None:
            payload["format"] = post_format
        if meta is not None:
            payload["meta"] = meta
        if sticky is not None:
            payload["sticky"] = sticky
        if template is not None:
            payload["template"] = template
        if categories is not None:
            payload["categories"] = categories
        if tags is not None:
            payload["tags"] = tags

        url = f"{self.base_url}/wp-json/wp/v2/posts/{post_id}"
        logger.info("Updating post %s with payload: %s", post_id, payload)
        response = requests.post(url, headers=self.headers, json=payload)
        logger.debug("Response: %s", response.text)
        if response.status_code != 200:
            logger.error("Failed to update post %s: %s %s", post_id, response.status_code, response.text)
            raise Exception(f"Failed to update post {post_id}: {response.status_code} {response.text}")
        logger.info("Post %s updated successfully", post_id)
        return response.json()

    def delete_post(self, post_id: int, force: bool = True) -> Dict[str, Any]:
        """
        Удаляет пост.

        :param post_id: Идентификатор поста для удаления
        :param force: Если True, пост удаляется сразу (без помещения в корзину)
        :return: JSON-ответ от сервера (ожидается статус 200)
        :raises Exception: Если удаление не удалось
        """
        url = f"{self.base_url}/wp-json/wp/v2/posts/{post_id}"
        params = {'force': 'true' if force else 'false'}
        logger.info("Deleting post %s with params: %s", post_id, params)
        response = requests.delete(url, headers=self.headers, params=params)
        logger.debug("Response: %s", response.text)
        if response.status_code != 200:
            logger.error("Failed to delete post %s: %s %s", post_id, response.status_code, response.text)
            raise Exception(f"Failed to delete post {post_id}: {response.status_code} {response.text}")
        logger.info("Post %s deleted successfully", post_id)
        return response.json()

    def list_posts(
            self,
            context: str = 'view',
            page: Optional[int] = None,
            per_page: Optional[int] = None,
            search: Optional[str] = None,
            after: Optional[str] = None,
            modified_after: Optional[str] = None,
            author: Optional[int] = None,
            author_exclude: Optional[List[int]] = None,
            before: Optional[str] = None,
            modified_before: Optional[str] = None,
            exclude: Optional[List[int]] = None,
            include: Optional[List[int]] = None,
            offset: Optional[int] = None,
            order: Optional[str] = None,
            orderby: Optional[str] = None,
            search_columns: Optional[List[str]] = None,
            slug: Optional[str] = None,
            status: Optional[str] = None,
            tax_relation: Optional[str] = None,
            categories: Optional[List[int]] = None,
            categories_exclude: Optional[List[int]] = None,
            tags: Optional[List[int]] = None,
            tags_exclude: Optional[List[int]] = None,
            sticky: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a list of posts from WordPress with optional filters.

        This method allows querying posts using various parameters such as search terms, author filters,
        date ranges, categories, tags, and sorting options.

        :param context: Scope under which the request is made ('view', 'embed', 'edit'). Defaults to 'view'.
        :param page: The current page of the collection.
        :param per_page: The maximum number of posts to return in the response.
        :param search: Limits results to posts matching the specified search string.
        :param after: Returns posts published after the specified ISO8601 date.
        :param modified_after: Returns posts modified after the specified ISO8601 date.
        :param author: Limits results to posts by the specified author ID.
        :param author_exclude: Excludes posts from the specified author(s).
        :param before: Returns posts published before the specified ISO8601 date.
        :param modified_before: Returns posts modified before the specified ISO8601 date.
        :param exclude: Excludes specific post IDs from the results.
        :param include: Limits results to specific post IDs.
        :param offset: Skips the first N posts in the response.
        :param order: Specifies sorting order ('asc' or 'desc').
        :param orderby: Sorts posts by a specific attribute ('date', 'title', 'id', etc.).
        :param search_columns: Limits the search to specific post fields.
        :param slug: Limits results to posts with the specified slug(s).
        :param status: Filters posts by status ('publish', 'draft', 'pending', 'private', etc.).
        :param tax_relation: Defines the relationship between multiple taxonomy queries ('AND' or 'OR').
        :param categories: Limits results to posts in specific category IDs.
        :param categories_exclude: Excludes posts in specific category IDs.
        :param tags: Limits results to posts with specific tag IDs.
        :param tags_exclude: Excludes posts with specific tag IDs.
        :param sticky: Filters results based on whether a post is marked as sticky.
        :return: A JSON response containing the list of posts.
        :raises Exception: If the request fails or an error occurs.
        """
        params: Dict[str, Any] = {'context': context}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if search is not None:
            params["search"] = search
        if after is not None:
            params["after"] = after
        if modified_after is not None:
            params["modified_after"] = modified_after
        if author is not None:
            params["author"] = author
        if author_exclude is not None:
            params["author_exclude"] = self._format_query_param(author_exclude)
        if before is not None:
            params["before"] = before
        if modified_before is not None:
            params["modified_before"] = modified_before
        if exclude is not None:
            params["exclude"] = self._format_query_param(exclude)
        if include is not None:
            params["include"] = self._format_query_param(include)
        if offset is not None:
            params["offset"] = offset
        if order is not None:
            params["order"] = order
        if orderby is not None:
            params["orderby"] = orderby
        if search_columns is not None:
            params["search_columns"] = self._format_query_param(search_columns)
        if slug is not None:
            params["slug"] = slug
        if status is not None:
            params["status"] = status
        if tax_relation is not None:
            params["tax_relation"] = tax_relation
        if categories is not None:
            params["categories"] = self._format_query_param(categories)
        if categories_exclude is not None:
            params["categories_exclude"] = self._format_query_param(categories_exclude)
        if tags is not None:
            params["tags"] = self._format_query_param(tags)
        if tags_exclude is not None:
            params["tags_exclude"] = self._format_query_param(tags_exclude)
        if sticky is not None:
            params["sticky"] = sticky

        url = f"{self.base_url}/wp-json/wp/v2/posts"
        logger.info("Listing posts with params: %s", params)
        response = requests.get(url, headers=self.headers, params=params)
        logger.debug("Response: %s", response.text)
        if response.status_code != 200:
            logger.error("Failed to list posts: %s %s", response.status_code, response.text)
            raise Exception(f"Failed to list posts: {response.status_code} {response.text}")
        logger.info("Posts listed successfully")
        return response.json()
