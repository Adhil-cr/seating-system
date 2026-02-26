from django.shortcuts import render

# Create your views here.

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import admin_required
from .models import Hall

@csrf_exempt
@admin_required
def create_hall(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)

    hall = Hall.objects.create(
        name=data.get("name"),
        rows=data.get("rows"),
        columns=data.get("columns"),
        seats_per_bench=data.get("seats_per_bench"),
    )

    return JsonResponse({
        "status": "hall created",
        "capacity": hall.capacity
    })