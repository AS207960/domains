from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as default_exception_handler
import grpc


class GRPCError(APIException):
    status_code = 500
    default_code = 'internal_error'


def exception_handler(exc, context):
    if isinstance(exc, grpc.RpcError):
        return default_exception_handler(GRPCError(
            detail=f"Error communicating with regitry: {exc.details()}"
        ), context)
    else:
        return default_exception_handler(exc, context)
