import logging


class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_exception(self, request, exception):
        logging.exception('Exception handling request for ' + request.path)
