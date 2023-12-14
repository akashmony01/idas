from django.urls import path

from .views import (
    not_found_404_view, dashboard_view, home_view, signup_view, profile_view,
    site_info_view, site_info_update_view, profile_update_view,
    preset_create_view, preset_details_view, preset_update_view,
    preset_slot_add_view, preset_slot_update_view, preset_slot_delete_view,
    preset_list_view, preset_delete_view, appointment_get_view,
    appointment_create_view, appointment_details_view, appointment_list_view,
    appointment_delete_view, appointment_update_view, appointment_file_add_view,
    appointment_file_update_view, appointment_file_delete_view, day_off_create_view,
    day_off_list_view, day_off_delete_view, day_off_details_view, day_off_update_view,
    appointment_list_today_view, appointment_view_view, appointment_mark_arrived_view,
    appointment_mark_cancelled_view, appointment_mark_completed_view,
    collaborator_create_view, collaborator_list_view, collaborator_delete_view,
    chamber_appointments_view, chamber_appointments_today_view, appointments_by_day_view
)

handler404 = not_found_404_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('accounts/signup/', signup_view, name='signup_alt'),

    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),

    path('profile/', profile_view, name='profile'),
    path('profile-update/', profile_update_view, name='profile_update'),


    path('accounts/profile/', profile_view, name='profile_alt'),
    path('site-info/', site_info_view, name='site_info'),
    path('site-info-update/', site_info_update_view, name='site_info_update'),

    path('chamber-create/', preset_create_view, name='preset_create'),
    path('chamber-details/<int:pk>/', preset_details_view, name='preset_details'),
    path('chamber-update/<int:pk>/', preset_update_view, name='preset_update'),

    path('chamber/<int:pk>/slot-add/', preset_slot_add_view, name='preset_slot_add'),
    path('chamber/<int:pk>/slot-update/', preset_slot_update_view, name='preset_slot_update'),
    path('chamber/<int:preset_pk>/slot-delete/<int:slot_pk>/', preset_slot_delete_view, name='preset_slot_delete'),

    path('chamber-list/', preset_list_view, name='preset_list'),
    path('chamber-delete/<int:pk>/', preset_delete_view, name='preset_delete'),

    path('appointment/', appointment_get_view, name='appointment_get'),
    path('appointment-create/<int:slot_pk>/<str:target_date>/', appointment_create_view, name='appointment_create'),
    path('appointment-details/<int:pk>/', appointment_details_view, name='appointment_details'),
    path('appointment-update/<int:pk>/', appointment_update_view, name='appointment_update'),

    path("appointment/<int:pk>/file-add", appointment_file_add_view, name="appointment_file_add"),
    path("appointment/<int:pk>/file-update", appointment_file_update_view, name="appointment_file_update"),
    path('appointment/<int:app_pk>/file-delete/<int:file_pk>/', appointment_file_delete_view, name='appointment_file_delete'),

    path('appointment-list/', appointment_list_view, name='appointment_list'),
    path('appointment-list-today/', appointment_list_today_view, name='appointment_list_today'),
    path('appointment-mark-arrived/<int:pk>/', appointment_mark_arrived_view, name='appointment_mark_arrived'),
    path('appointment-mark-completed/<int:pk>/', appointment_mark_completed_view, name='appointment_mark_completed'),
    path('appointment-mark-cancelled/<int:pk>/', appointment_mark_cancelled_view, name='appointment_mark_cancelled'),

    path('appointment-delete/<int:pk>/', appointment_delete_view, name='appointment_delete'),
    path('appointment-view/<int:pk>/', appointment_view_view, name='appointment_view'),

    path('day-off-create/', day_off_create_view, name='day_off_create'),
    path('day-off-list/', day_off_list_view, name='day_off_list'),

    path('day-off-delete/<int:pk>/', day_off_delete_view, name='day_off_delete'),
    path('day-off-details/<int:pk>/', day_off_details_view, name='day_off_details'),
    path('day-off-update/<int:pk>/', day_off_update_view, name='day_off_update'),

    path('collaborator-create/', collaborator_create_view, name='collaborator_create'),
    path('collaborator-list/', collaborator_list_view, name='collaborator_list'),
    path('collaborator-delete/<int:pk>/', collaborator_delete_view, name='collaborator_delete'),

    path('chamber-appointments/', chamber_appointments_view, name='chamber_appointments'),
    path('chamber-appointments-today/', chamber_appointments_today_view, name='chamber_appointments_today'),
    path('appointments-by-day/', appointments_by_day_view, name='appointments_by_day'),
]