from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from jobsection.models import JobPostings,Applications_received,Profile
from django.db.models import Count
from django.shortcuts import get_object_or_404
from usersection.models import Userinfo
from django.contrib import messages


# Create your views here.

def jobdashboard(request):
    total_jobpostings=JobPostings.objects.all().count()
    active_profiles=Profile.objects.all().count()
    total_applications=Applications_received.objects.all().count()
    job_categories = JobPostings.objects.values('Job_Category').distinct().count()

    recruiters = JobPostings.objects.values('User').distinct().count()

    context = {
        'total_jobpostings': total_jobpostings,
        'active_profiles': active_profiles,
        'total_applications': total_applications,
        'recruiters': recruiters,
        'job_categories':job_categories
    }
    return render(request, 'jobadmin/jobdashboard.html', context)

def posted_jobs(request):
    jobs=JobPostings.objects.all().order_by('-Posted_Date')
    
    return render(request,'jobadmin/postedjob.html',{'posted_job':jobs}) 

def job_detail(request,id):
    detail=JobPostings.objects.filter(id=id).first()
    return render(request,'jobadmin/jobsdetail.html',{'jobdetails':detail})

def recruiterdetail(request,id):
    recruiter=JobPostings.objects.filter(id=id).first()
    recruiterid=recruiter.User
    profile=Profile.objects.filter(User=recruiterid).first()
    return render(request,'jobadmin/recruiterdetail.html',{'recruiter':profile})

def applied_candidates(request,id):
    job_posting = get_object_or_404(JobPostings, id=id)

    applied_candidates=Applications_received.objects.filter(Posted_by=job_posting).order_by('-Applied_date')
    return render(request,'jobadmin/appliedusers.html',{'applied_users':applied_candidates})

def view_detail_application(request,id):
    
    detail_profile=get_object_or_404(Profile, id=id)
    user=Applications_received.objects.filter(Applicant_profile=detail_profile).first()

    return render(request,'jobadmin/viewapplieddata.html',{'detail':detail_profile,'user':user})

def active_profile(request):
    profiles=Profile.objects.all()
    return render (request,'jobadmin/activeprofile.html',{'profiles':profiles})

def applied_jobs(request,id):
    applied_jobs=Applications_received.objects.filter(Applicant=id)
    return render(request,'jobadmin/apliedjobs.html',{'jobsapplied':applied_jobs})


def recruiters(request):
    postings = JobPostings.objects.all()
    users = postings.values_list('User', flat=True).distinct()  
    profiles = Profile.objects.filter(User__in=users)  
    return render(request, 'jobadmin/recruiters.html', {'profiles': profiles})

def categories(request):
    category = JobPostings.objects.values_list('Job_Category', flat=True).distinct()  
    return render(request,'jobadmin/jobcategories.html',{'categories':category})


def categoried_jobs(request, category):
    jobs = JobPostings.objects.filter(Job_Category=category)

    return render(request, 'jobadmin/categoriedjob.html', {'jobs': jobs, 'category': category})

def totalapplication(request):
    application=Applications_received.objects.all()
    return render(request,'jobadmin/totalapplications.html',{'applications':application})

def deletejob(request, id):
    job = get_object_or_404(JobPostings, id=id)  # Get the job or return a 404

    # Delete the job directly
    job.delete()
    messages.success(request, 'Job deleted successfully.')  # Success message
    return redirect('postedjobs') 