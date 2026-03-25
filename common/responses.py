from rest_framework import status
from rest_framework.response import Response


def success_response(*, message="success", data=None, status_code=status.HTTP_200_OK):
    return Response(
        {
            "code": status_code,
            "message": message,
            "data": data,
        },
        status=status_code,
    )

