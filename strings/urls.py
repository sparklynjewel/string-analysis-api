from django.urls import path
from . import views

urlpatterns = [
    path('strings/', views.create_string, name='create_string'),
    path('strings/<str:string_value>', views.get_string, name='get_string'),
    path('strings/<str:string_value>', views.delete_string, name='delete_string'),
    path('strings/filter-by-natural-language', views.filter_by_natural_language, name='filter_by_natural_language'),
    path('strings/list', views.list_strings, name='list_strings'),  # optional: or use `/strings/` for listing
]
