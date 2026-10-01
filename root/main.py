import logging 
from model.main import Model
from model.scripts import log_builder


if __name__ == '__main__':
    logger = logging.getLogger()
    log_builder.logger_setup(logger)
    model = Model()
    model.start_routine()
