from django.db import models
from django.contrib.auth.models import AbstractUser
import random

class User(AbstractUser):
    # Role & Location
    is_department_admin = models.BooleanField(default=False)
    department_name = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, default="Indore")
    is_blocked = models.BooleanField(default=False)  # Added to fix database constraint
    is_verified = models.BooleanField(default=False)  # Added to fix database constraint 
    
    # Profile Data
    phone = models.CharField(max_length=15, blank=True, null=True)
    aadhar_id = models.CharField(max_length=12, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

class Complaint(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Solved', 'Solved'), ('Closed', 'Closed')]
    PRIORITY_CHOICES = [('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]
    RESOLUTION_CHOICES = [('Fully Resolved', 'Fully Resolved'), ('Partially Resolved', 'Partially Resolved'), ('Not Resolved', 'Not Resolved')]

    # Smart Ticket ID (e.g. 10492)
    ticket_id = models.IntegerField(unique=True, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    location_name = models.CharField(max_length=200)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=50) # Snapshot of city
    title = models.CharField(blank=True, max_length=200)
    image = models.ImageField(upload_to='complaints/', blank=True, null=True)
    
    department = models.CharField(max_length=50) 
    CATEGORY_CHOICES = [
        ('Road/Street', 'Road/Street'),
        ('Water/Sewage', 'Water/Sewage'),
        ('Electricity', 'Electricity'),
        ('Garbage', 'Garbage'),
        ('Health', 'Health'),
        ('Safety', 'Safety'),
        ('Parks', 'Parks'),       
        ('Other', 'Other'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Low')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_escalated = models.BooleanField(default=False)
    sla_breached = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    similar_complaints_count = models.IntegerField(default=0)

    # Geo & Feedback
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    resolution = models.CharField(max_length=20, choices=RESOLUTION_CHOICES, blank=True, null=True)
    
    # Feedback System
    feedback = models.TextField(blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)  # 1-5 stars
    feedback_submitted_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    solved_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 1. Generate ID if not present
        if not self.ticket_id:
            prefix = 90
            if self.department == 'Municipal': prefix = 10
            elif self.department == 'Police': prefix = 20
            elif self.department == 'Electricity': prefix = 30
            elif self.department == 'Health': prefix = 40
            elif self.department == 'Water': prefix = 50
            elif self.department == 'PWD': prefix = 60
            self.ticket_id = int(f"{prefix}{random.randint(100, 999)}")

        # 2. Auto-fill City from User
        if not self.city and self.user:
            self.city = self.user.city
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.ticket_id} - {self.description[:20]}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default='Notification')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)