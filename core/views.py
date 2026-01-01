from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField, Count, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from .models import User, Complaint, Notification
from .ai_model.engine import ai_bot
import json
from datetime import datetime, timedelta

# --- UTILS ---
def send_notif(user, message):
    Notification.objects.create(user=user, message=message)

# --- AUTH ---
def auth_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login':
            u = request.POST.get('username')
            p = request.POST.get('password')
            user = authenticate(username=u, password=p)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'auth.html', {'error': 'Invalid Credentials'})
        elif action == 'signup':
            try:
                role = request.POST.get('role')
                u = request.POST.get('username')
                p = request.POST.get('password')
                phone = request.POST.get('phone', '')
                city = request.POST.get('city', 'Indore')
                aadhar = request.POST.get('aadhar_id', '')
                address = request.POST.get('address', '')
                
                if role == 'admin':
                    dept = request.POST.get('department', '')
                    user = User.objects.create_user(
                        username=u, 
                        password=p, 
                        is_department_admin=True, 
                        department_name=dept, 
                        phone=phone, 
                        city=city,
                        aadhar_id=aadhar,
                        address=address
                    )
                else:
                    user = User.objects.create_user(
                        username=u, 
                        password=p, 
                        is_department_admin=False, 
                        phone=phone, 
                        city=city,
                        aadhar_id=aadhar,
                        address=address
                    )
                login(request, user)
                return redirect('dashboard')
            except Exception as e:
                return render(request, 'auth.html', {'error': str(e)})
    return render(request, 'auth.html')

def logout_view(request):
    logout(request)
    return redirect('auth')

# --- PROFILE LOGIC ---
@login_required
def update_profile_pic(request):
    if request.method == 'POST' and request.FILES.get('profile_pic'):
        request.user.profile_pic = request.FILES['profile_pic']
        request.user.save()
    return redirect('dashboard')

@login_required
def profile_view(request):
    user = request.user
    if user.is_department_admin:
        # Show admin's department complaints
        complaints = Complaint.objects.filter(department=user.department_name, city__iexact=user.city).order_by('-created_at')
        return render(request, 'admin_profile.html', {'user': user, 'complaints': complaints})
    else:
        return render(request, 'profile.html', {'user': user})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.aadhar_id = request.POST.get('aadhar_id', user.aadhar_id)
        user.address = request.POST.get('address', user.address)
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES['profile_pic']
        user.save()
        return redirect('profile_view')
    return redirect('dashboard')

# --- DASHBOARD ---
@login_required
def dashboard_view(request):
    user = request.user
    notifs = Notification.objects.filter(user=user).order_by('-created_at')[:5]
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    priority_order = Case(When(priority='High', then=Value(1)), When(priority='Medium', then=Value(2)), When(priority='Low', then=Value(3)), output_field=IntegerField())

    # ADMIN VIEW
    if user.is_department_admin:
        complaints = Complaint.objects.filter(department=user.department_name, city__iexact=user.city).annotate(sort=priority_order).order_by('sort', '-created_at')
        active_complaints = complaints.exclude(status='Closed')  # Active cases only
        closed_complaints = complaints.filter(status='Closed')
        fully_resolved = closed_complaints.filter(resolution='Fully Resolved').count()
        
        # Calculate resolution percentage
        resolved_percentage = 0
        if closed_complaints.count() > 0:
            resolved_percentage = int((fully_resolved / closed_complaints.count()) * 100)
        
        hotspots = complaints.values('pincode', 'location_name').annotate(total=Count('id')).order_by('-total')[:5]
        map_data = list(complaints.exclude(latitude__isnull=True).exclude(status='Closed').values('ticket_id', 'description', 'latitude', 'longitude', 'priority', 'status', 'user__username', 'user__phone'))
        
        p_data = [complaints.filter(priority='High').count(), complaints.filter(priority='Medium').count(), complaints.filter(priority='Low').count()]
        s_data = [complaints.filter(status='Pending').count(), complaints.filter(status='Solved').count(), complaints.filter(status='Closed').count()]

        return render(request, 'dash_admin.html', {
            'complaints': complaints, 
            'active_count': active_complaints.count(),
            'resolved_percentage': resolved_percentage,
            'hotspots': hotspots, 
            'chart_prio': json.dumps(p_data), 
            'chart_status': json.dumps(s_data), 
            'map_data': json.dumps(map_data), 
            'notifs': notifs, 
            'unread_count': unread_count
        })

    # USER VIEW
    else:
        complaints = Complaint.objects.filter(user=user).order_by('-created_at')
        closed_count = complaints.filter(status='Closed').count()
        
        # NEW PROFESSIONAL LOGIC
        level = "Active Resident"          # Level 1 (Entry)
        if closed_count > 5: 
            level = "Civic Steward"        # Level 2 (Intermediate)
        if closed_count > 15: 
            level = "Community Ambassador" # Level 3 (Top Tier)

        stats = {
            'total': complaints.count(),
            'pending': complaints.filter(status='Pending').count(),
            'solved': complaints.filter(status='Solved').count(),
            'closed': closed_count,
            'level': level
        }
        return render(request, 'dash_user.html', {
            'complaints': complaints, 'stats': stats, 'notifs': notifs, 'unread_count': unread_count
        })
# --- COMPLAINT ACTIONS ---
@login_required
def submit_complaint(request):
    if request.method == 'POST':
        desc = request.POST.get('description')
        loc = request.POST.get('location_name')
        pin = request.POST.get('pincode')
        img = request.FILES.get('image')
        lat = request.POST.get('latitude') or None
        lng = request.POST.get('longitude') or None
        
        # Improved AI prediction (confidence not shown to user)
        dept, prio, confidence = ai_bot.predict(desc)
        Complaint.objects.create(
            user=request.user, 
            description=desc, 
            location_name=loc, 
            pincode=pin, 
            image=img, 
            department=dept, 
            priority=prio, 
            latitude=lat, 
            longitude=lng, 
            city=request.user.city,
            category=request.POST.get('category', 'Other'),
            is_escalated=False,
            sla_breached=False,
            is_public=True,
            views_count=0,
            similar_complaints_count=0
        )
        # Removed confidence score from user notification
        send_notif(request.user, f"✅ Complaint submitted! Assigned to {dept}")
    return redirect('dashboard')

@login_required
def mark_solved(request, id):
    c = get_object_or_404(Complaint, id=id)
    if request.user.is_department_admin:
        c.status = 'Solved'
        c.solved_at = timezone.now()
        c.save()
        send_notif(c.user, f"✅ Ticket #{c.ticket_id} resolved. Please provide feedback!")
    return redirect('dashboard')

@login_required
def verify_close(request, id):
    c = get_object_or_404(Complaint, id=id)
    if c.user == request.user:
        if request.method == 'POST':
            # Get resolution status from form
            resolution = request.POST.get('resolution')
            feedback = request.POST.get('feedback')
            rating = request.POST.get('rating', None)
            
            c.resolution = resolution
            c.feedback = feedback
            if rating:
                c.rating = int(rating)
            c.feedback_submitted_at = timezone.now()
            c.status = 'Closed'
            c.closed_at = timezone.now()
            c.save()
            
            send_notif(c.user, f"✅ Thank you! Ticket #{c.ticket_id} closed. Your feedback helps us improve!")
    return redirect('dashboard')

@login_required
def transfer_complaint(request, id):
    if request.method == 'POST':
        c = get_object_or_404(Complaint, id=id)
        if request.user.is_department_admin:
            c.department = request.POST.get('new_department')
            c.save()
    return redirect('dashboard')

@login_required
def reopen_complaint(request, id):
    c = get_object_or_404(Complaint, id=id)
    if c.user == request.user:
        c.status = 'Pending'
        c.closed_at = None
        c.save()
        send_notif(c.user, f"Ticket #{c.ticket_id} reopened for review.")
    return redirect('dashboard')

# ============ NEW FEATURES (10+) ============

# FEATURE 1: User Complaint History Timeline
@login_required
def complaint_timeline(request, id):
    """Show detailed timeline of complaint status changes"""
    complaint = get_object_or_404(Complaint, id=id)
    
    if complaint.user != request.user and request.user.department_name != complaint.department:
        return redirect('dashboard')
    
    timeline = []
    if complaint.created_at:
        timeline.append({
            'status': 'Submitted',
            'time': complaint.created_at,
            'icon': 'fa-paper-plane',
            'color': 'blue'
        })
    if complaint.solved_at:
        timeline.append({
            'status': 'Resolved',
            'time': complaint.solved_at,
            'icon': 'fa-check-circle',
            'color': 'green'
        })
    if complaint.feedback_submitted_at:
        timeline.append({
            'status': 'Feedback Given',
            'time': complaint.feedback_submitted_at,
            'icon': 'fa-star',
            'color': 'yellow'
        })
    if complaint.closed_at:
        timeline.append({
            'status': 'Closed',
            'time': complaint.closed_at,
            'icon': 'fa-lock',
            'color': 'gray'
        })
    
    return render(request, 'complaint_timeline.html', {
        'complaint': complaint,
        'timeline': timeline
    })

# FEATURE 2: Search & Filter Complaints
@login_required
def search_complaints(request):
    """Search complaints by keyword, status, priority, date range"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if request.user.is_department_admin:
        complaints = Complaint.objects.filter(department=request.user.department_name, city__iexact=request.user.city)
    else:
        complaints = Complaint.objects.filter(user=request.user)
    
    if query:
        complaints = complaints.filter(Q(description__icontains=query) | Q(location_name__icontains=query) | Q(ticket_id__icontains=query))
    if status:
        complaints = complaints.filter(status=status)
    if priority:
        complaints = complaints.filter(priority=priority)
    if date_from:
        complaints = complaints.filter(created_at__gte=date_from)
    if date_to:
        complaints = complaints.filter(created_at__lte=date_to)
    
    return render(request, 'search_results.html', {
        'complaints': complaints,
        'query': query,
        'count': complaints.count()
    })

# FEATURE 3: Statistics & Analytics
@login_required
def analytics_view(request):
    """Show detailed analytics and statistics"""
    user = request.user
    
    if user.is_department_admin:
        complaints = Complaint.objects.filter(department=user.department_name, city__iexact=user.city)
        
        stats = {
            'total': complaints.count(),
            'pending': complaints.filter(status='Pending').count(),
            'solved': complaints.filter(status='Solved').count(),
            'closed': complaints.filter(status='Closed').count(),
            'high_priority': complaints.filter(priority='High').count(),
            'avg_rating': complaints.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg'] or 0,
            'resolution_rate': 0
        }
        
        closed = complaints.filter(status='Closed')
        if closed.count() > 0:
            fully = closed.filter(resolution='Fully Resolved').count()
            stats['resolution_rate'] = int((fully / closed.count()) * 100)
        
        # Last 7 days
        last_7_days = timezone.now() - timedelta(days=7)
        recent = complaints.filter(created_at__gte=last_7_days).count()
        
        return render(request, 'analytics.html', {
            'stats': stats,
            'recent_complaints': recent,
            'complaints': complaints[:10]
        })
    else:
        complaints = Complaint.objects.filter(user=user)
        stats = {
            'total': complaints.count(),
            'pending': complaints.filter(status='Pending').count(),
            'solved': complaints.filter(status='Solved').count(),
            'closed': complaints.filter(status='Closed').count(),
        }
        return render(request, 'user_analytics.html', {'stats': stats})

# FEATURE 4: Export Complaints
@login_required
def export_complaints(request):
    """Export complaints to CSV"""
    import csv
    from django.http import HttpResponse
    
    if request.user.is_department_admin:
        complaints = Complaint.objects.filter(department=request.user.department_name, city__iexact=request.user.city)
    else:
        complaints = Complaint.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="complaints.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Ticket ID', 'Description', 'Location', 'Status', 'Priority', 'Created', 'Resolved', 'Feedback', 'Rating'])
    
    for c in complaints:
        writer.writerow([
            c.ticket_id, c.description, c.location_name, c.status, c.priority,
            c.created_at.strftime('%Y-%m-%d %H:%M') if c.created_at else '',
            c.solved_at.strftime('%Y-%m-%d %H:%M') if c.solved_at else '',
            c.feedback or '', c.rating or ''
        ])
    
    return response

# FEATURE 5: Department Performance
@login_required
def department_stats(request):
    """Show department-wise statistics (for admins)"""
    if not request.user.is_department_admin:
        return redirect('dashboard')
    
    dept_complaints = Complaint.objects.filter(department=request.user.department_name)
    
    stats = {
        'avg_resolution_time': 0,
        'feedback_average': dept_complaints.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg'] or 0,
        'total_feedback': dept_complaints.filter(feedback__isnull=False).count(),
        'performance_score': 0
    }
    
    # Calculate avg resolution time (in hours)
    resolved = dept_complaints.filter(solved_at__isnull=False)
    if resolved.exists():
        total_hours = sum([(c.solved_at - c.created_at).total_seconds() / 3600 for c in resolved])
        stats['avg_resolution_time'] = int(total_hours / resolved.count())
    
    # Performance score = (Avg Rating * 20) + (Feedback % * 0.8) + (Closure Rate * 20)
    if dept_complaints.count() > 0:
        feedback_pct = (stats['total_feedback'] / dept_complaints.count()) * 100
        closure_rate = (dept_complaints.filter(status='Closed').count() / dept_complaints.count()) * 100
        stats['performance_score'] = int((stats['feedback_average'] * 20) + (feedback_pct * 0.08) + (closure_rate * 0.2))
    
    return render(request, 'department_stats.html', {
        'stats': stats,
        'department': request.user.department_name
    })

# FEATURE 6: Feedback Dashboard (Admin can see all feedback)
@login_required
def feedback_dashboard(request):
    """Show all user feedback for resolved complaints"""
    if not request.user.is_department_admin:
        return redirect('dashboard')
    
    feedback_list = Complaint.objects.filter(
        department=request.user.department_name,
        city__iexact=request.user.city,
        feedback__isnull=False
    ).exclude(feedback='').order_by('-feedback_submitted_at')
    
    feedback_stats = {
        'total_feedback': feedback_list.count(),
        'avg_rating': feedback_list.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg'] or 0,
        'fully_resolved_feedback': feedback_list.filter(resolution='Fully Resolved').count(),
        'partially_resolved_feedback': feedback_list.filter(resolution='Partially Resolved').count(),
        'not_resolved_feedback': feedback_list.filter(resolution='Not Resolved').count(),
    }
    
    return render(request, 'feedback_dashboard.html', {
        'feedback_list': feedback_list,
        'feedback_stats': feedback_stats
    })

# FEATURE 7: Complaint Status Update (Real-time)
@login_required
def quick_update_status(request, id):
    """Quick status update without page reload (AJAX)"""
    complaint = get_object_or_404(Complaint, id=id)
    
    if not request.user.is_department_admin or complaint.department != request.user.department_name:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Solved', 'Closed']:
            complaint.status = new_status
            if new_status == 'Solved' and not complaint.solved_at:
                complaint.solved_at = timezone.now()
            complaint.save()
            return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# FEATURE 8: Download Complaint Details
@login_required
def download_complaint(request, id):
    """Download single complaint as PDF"""
    from django.http import HttpResponse
    complaint = get_object_or_404(Complaint, id=id)
    
    if complaint.user != request.user and request.user.department_name != complaint.department:
        return redirect('dashboard')
    
    # Simple text format for now (can be extended to PDF)
    content = f"""
COMPLAINT DETAILS
================
Ticket ID: {complaint.ticket_id}
Created: {complaint.created_at.strftime('%Y-%m-%d %H:%M:%S') if complaint.created_at else 'N/A'}
Status: {complaint.status}
Priority: {complaint.priority}
Department: {complaint.department}

DESCRIPTION:
{complaint.description}

LOCATION:
{complaint.location_name}, {complaint.pincode}
Coordinates: {complaint.latitude}, {complaint.longitude}

FEEDBACK:
{complaint.feedback or 'No feedback yet'}
Rating: {complaint.rating or 'Not rated'}/5
Resolution: {complaint.resolution or 'Not resolved'}

TIMELINE:
Submitted: {complaint.created_at}
Resolved: {complaint.solved_at or 'Pending'}
Closed: {complaint.closed_at or 'Open'}
"""
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="complaint_{complaint.ticket_id}.txt"'
    return response

# FEATURE 9: Similar Complaints
@login_required
def similar_complaints(request, id):
    """Show similar complaints in same area"""
    complaint = get_object_or_404(Complaint, id=id)
    
    similar = Complaint.objects.filter(
        pincode=complaint.pincode,
        department=complaint.department
    ).exclude(id=id)[:5]
    
    return render(request, 'similar_complaints.html', {
        'complaint': complaint,
        'similar_complaints': similar
    })

# FEATURE 10: Notification Preferences
@login_required
def notification_settings(request):
    """Manage notification preferences"""
    user = request.user
    
    if request.method == 'POST':
        # Save preferences (can be extended with more granular options)
        prefs = {
            'email_on_update': request.POST.get('email_on_update', False),
            'sms_on_update': request.POST.get('sms_on_update', False),
            'digest_frequency': request.POST.get('digest_frequency', 'instant')
        }
        # Store in session or user profile (if extended model)
        request.session['notification_prefs'] = prefs
        return render(request, 'notification_settings.html', {'saved': True})
    
    return render(request, 'notification_settings.html', {'saved': False})

# FEATURE 11: Track Complaint Live Map
@login_required
def complaint_heatmap(request):
    """Show heatmap of complaints by location"""
    if request.user.is_department_admin:
        complaints = Complaint.objects.filter(
            department=request.user.department_name,
            city__iexact=request.user.city
        ).exclude(latitude__isnull=True)
    else:
        complaints = Complaint.objects.filter(user=request.user).exclude(latitude__isnull=True)
    
    heatmap_data = [{
        'lat': float(c.latitude),
        'lng': float(c.longitude),
        'title': f"#{c.ticket_id}: {c.description[:30]}",
        'priority': c.priority
    } for c in complaints]
    
    return render(request, 'complaint_heatmap.html', {
        'heatmap_data': json.dumps(heatmap_data),
        'complaint_count': len(heatmap_data)
    })

# FEATURE 12: Bulk Actions
@login_required
def bulk_action(request):
    """Perform bulk actions on multiple complaints"""
    if not request.user.is_department_admin:
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        complaint_ids = request.POST.getlist('complaint_ids')
        
        complaints = Complaint.objects.filter(id__in=complaint_ids, department=request.user.department_name)
        
        if action == 'mark_solved':
            complaints.update(status='Solved', solved_at=timezone.now())
            send_notif(request.user, f"✅ {complaints.count()} complaints marked as solved")
        elif action == 'change_priority':
            new_priority = request.POST.get('priority')
            complaints.update(priority=new_priority)
            send_notif(request.user, f"✅ {complaints.count()} complaints priority updated")
        elif action == 'transfer':
            new_dept = request.POST.get('department')
            complaints.update(department=new_dept)
            send_notif(request.user, f"✅ {complaints.count()} complaints transferred")
    
    return redirect('dashboard')