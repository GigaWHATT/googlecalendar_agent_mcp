"""Main module for g-calendar."""

# ------IMPORTS---------
from loguru import logger


def main():
    """Main function, prints a greeting."""
    logger.info("Hello from g-calendar!")
    return None


# -----------RUN-------------
if __name__ == "__main__":
    # Run the main function when the script is executed.
    main()
