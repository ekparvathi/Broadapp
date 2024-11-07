from django.urls import path
from jobadmin import views
urlpatterns = [
    path('jobdashboard/',views.jobdashboard,name="jobadash"),
    path('postedjobs/',views.posted_jobs,name="postedjobs"),
    path('detailview/<int:id>',views.job_detail,name="detailview"),
    path('recruiterinfo/<int:id>',views.recruiterdetail,name="recruiterdetail"),
    path('appliedusers/<int:id>',views.applied_candidates,name="applieduser"),
    path('detailviewapplicant/<int:id>',views.view_detail_application,name="detailprofile"),
    path('activeprofiles/',views.active_profile,name="activeprofiles"),
    path('appliedjobs/<int:id>',views.applied_jobs,name="jobsapplied"),
    path('recruiters/',views.recruiters,name="recruiters"),
    path('categories/',views.categories,name="category"),
    path('getcategorised/<str:category>',views.categoried_jobs,name="categorisedjob"),
    path('totalapplications/',views.totalapplication,name="totalapplication"),
    path('deletejob/<int:id>',views.deletejob,name="delete_job")
    
]