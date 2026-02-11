from django.http import JsonResponse

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "login required"}, status=401)

        if request.user.role not in ["admin", "super_admin"]:
            return JsonResponse({"error": "admin access only"}, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "login required"}, status=401)

        if request.user.role != "super_admin":
            return JsonResponse({"error": "super admin only"}, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper
