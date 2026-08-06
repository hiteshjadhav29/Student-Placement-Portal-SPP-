from functools import wraps

def placement_officer_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        print("User:", request.user.username)
        print("Role:", request.user.role)

        return view_func(request, *args, **kwargs)

    return wrapper