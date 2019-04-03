import logging

def sigintHandler(signal, frame):
    """
    Handles SIGINT by closing log and exiting
    """

    logging.info("SIGINT Handled")
    exit(0)

