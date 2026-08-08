from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):

    total_students = 2500
    total_companies = 150
    total_jobs = 300
    total_placements = 900
    placement_rate = 95.0
    featured_jobs = []

    try:
        from students.models import StudentProfile
        from recruiters.models import Company
        from jobs.models import Job
        from applications.models import Application

        s_count = StudentProfile.objects.count()
        c_count = Company.objects.count()
        j_count = Job.objects.count()
        p_count = Application.objects.filter(status='Selected').count()

        if s_count > 0: total_students = s_count
        if c_count > 0: total_companies = c_count
        if j_count > 0: total_jobs = j_count
        if p_count > 0: total_placements = p_count

        if s_count > 0:
            placement_rate = round((total_placements / total_students) * 100, 1)

        featured_jobs = Job.objects.filter(status='Open').select_related('company').order_by('-created_at')[:3]
    except Exception:
        pass

    context = {
        "total_students": total_students,
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "total_placements": total_placements,
        "placement_rate": placement_rate,
        "featured_jobs": featured_jobs,
    }

    return render(request, "home.html", context)