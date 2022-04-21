def add_append_user_to_data(request):
    data = request.data
    data['user'] = request.user.id
    return data