import logging

def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.

    Args:
        verbose (bool): If True, set logging level to DEBUG, else INFO.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s | %(message)s'
    )