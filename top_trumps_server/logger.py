import logging

def info_logger(websocket, message):
    # Create and configure logger
    logging.basicConfig(filename="./logs/conection_log.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
    
    # Creating an object
    logger = logging.getLogger()
    
    # Setting the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)

    logger.info(f'Message - {message}')
