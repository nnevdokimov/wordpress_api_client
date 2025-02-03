try:
    import trackrace
    logger = trackrace.get_logger("wordpress_api_client")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("wordpress_api_client")
