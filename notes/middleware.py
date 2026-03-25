import time
import uuid


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        request.request_id = request_id
        start_time = time.perf_counter()

        response = self.get_response(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        print(
            f"[request_id={request_id}] "
            f"{request.method} {request.path} "
            f"status={response.status_code} "
            f"duration_ms={duration_ms:.2f}"
        )

        response["X-Request-ID"] = request_id
        return response