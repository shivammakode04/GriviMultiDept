from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    # Auth
    path('', views.auth_view, name='auth'),
    path('logout-user/', views.logout_view, name='user_logout'),
    path('accounts/', include('django.contrib.auth.urls')),

    # Dashboard & Profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('update_pic/', views.update_profile_pic, name='update_profile_pic'),

    # Core Actions
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('solve/<int:id>/', views.mark_solved, name='mark_solved'),
    path('verify/<int:id>/', views.verify_close, name='verify_close'),
    path('transfer/<int:id>/', views.transfer_complaint, name='transfer_complaint'),
    path('reopen/<int:id>/', views.reopen_complaint, name='reopen_complaint'),

    # NEW FEATURES (10+)
    # 1. Complaint Timeline
    path('complaint/<int:id>/timeline/', views.complaint_timeline, name='complaint_timeline'),
    
    # 2. Search & Filter
    path('search/', views.search_complaints, name='search_complaints'),
    
    # 3. Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # 4. Export
    path('export/', views.export_complaints, name='export_complaints'),
    
    # 5. Department Stats
    path('dept-stats/', views.department_stats, name='department_stats'),
    
    # 6. Feedback Dashboard
    path('feedback/', views.feedback_dashboard, name='feedback_dashboard'),
    
    # 7. Quick Status Update
    path('complaint/<int:id>/status/', views.quick_update_status, name='quick_update_status'),
    
    # 8. Download Complaint
    path('complaint/<int:id>/download/', views.download_complaint, name='download_complaint'),
    
    # 9. Similar Complaints
    path('complaint/<int:id>/similar/', views.similar_complaints, name='similar_complaints'),
    
    # 10. Notification Settings
    path('notifications/settings/', views.notification_settings, name='notification_settings'),
    
    # 11. Complaint Heatmap
    path('heatmap/', views.complaint_heatmap, name='complaint_heatmap'),
    
    # 12. Bulk Actions
    path('bulk-action/', views.bulk_action, name='bulk_action'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)