from django.urls import path
from .views import (
    home_view, signup_view, profile_view,
    preset_create_view, preset_details_view, preset_update_view,
    preset_slot_add_view, preset_slot_update_view, preset_slot_delete_view,
    preset_list_view, preset_delete_view, appointment_get_view
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('accounts/signup/', signup_view, name='signup_alt'),

    path('', home_view, name='home'),
    path('profile/', profile_view, name='profile'),
    path('accounts/profile/', profile_view, name='profile_alt'),

    path('preset-create/', preset_create_view, name='preset_create'),
    path('preset-details/<int:pk>/', preset_details_view, name='preset_details'),
    path('preset-update/<int:pk>/', preset_update_view, name='preset_update'),

    path('preset/<int:pk>/slot-add/', preset_slot_add_view, name='preset_slot_add'),
    path('preset/<int:pk>/slot-update/', preset_slot_update_view, name='preset_slot_update'),
    path('preset/<int:preset_pk>/slot-delete/<int:slot_pk>/', preset_slot_delete_view, name='preset_slot_delete'),

    path('preset-list/', preset_list_view, name='preset_list'),
    path('preset/', preset_list_view, name='preset_list_alt'),
    path('preset-delete/<int:pk>/', preset_delete_view, name='preset_delete'),

    path('appointment/', appointment_get_view, name='appointment_get'),
]