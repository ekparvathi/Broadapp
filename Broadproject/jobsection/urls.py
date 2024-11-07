from django.contrib import admin
from django.urls import path
from jobsection import views
urlpatterns = [
    path('uploadjobpost/',views.uploadjobpost,name="uploadnewjob"),
    path('displayjobs/',views.Display_jobs,name="displayjobs"),
    path('savejob/<int:id>',views.Saved_job,name="Savedjob"),
    path('displaysavedjobs/',views.Display_Saved_Jobs,name="displaysavedjobs"),
    path('searchjobs/',views.search_by_jobtitle,name="searchjob"),
    path('displaypostedjobs/',views.Display_Job_Posted,name="displayposted"),
    path('filter/',views.Filteration,name="jobfiltering"),
    path('createprofile/',views.create_profile,name="create-profile"),
    path('showprofile/',views.Show_profile,name="Showprofile"),
    path('applyjob/<int:id>',views.apply_job,name='applyjob'),
    path('showreceivedapplication/',views.received_application,name="receivedapplication"),
    path('detailapplication/<int:id>',views.application_detail,name="detailedapplication"),
    path('appliedjobs/',views.applied_jobs,name="appliedjobs"),
    path('recommendedjobs/',views.recommeded_jobs,name="recommendedjobs"),
    path('deletejobspost/<int:id>',views.deletejobposting,name="deletejobpost"),
    path('editjobpost/<int:id>',views.Editjobpost,name="editjobpost")
    
]