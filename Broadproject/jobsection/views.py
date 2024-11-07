from django.shortcuts import render
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from usersection.models import Userinfo
from rest_framework.response import Response
from .serializers import jobpostserializer,ProfileSerializer,applyserializer
from rest_framework import status
from .models import JobPostings,Saved_Jobs,Profile,Applications_received
from django.db import IntegrityError
from django.utils.timesince import timesince



# Create your views here.

@api_view(['POST'])
def uploadjobpost(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=get_object_or_404(Userinfo,Email=current_user)
    else:
        return Response({'msg':'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    request.data['User'] = user.id 
    createjobpost=jobpostserializer(data=request.data)
    if createjobpost.is_valid():
        createjobpost.save()
        return Response({'msg':'Job Vaccancy Posted'},status=status.HTTP_200_OK)
    else:
        return Response({'msg':'somthing went wrong' ,'errors': createjobpost.errors},status=status.HTTP_400_BAD_REQUEST)
    



@api_view(['GET'])
def Display_jobs(request):
    # Query to get all job postings, sorted by Posted_Date descending (newest first)
    jobs = JobPostings.objects.all().order_by('-Posted_Date')  # Use '-' to sort in descending order
    
    # Add a human-readable time ago field directly to the serialized data
    job_data = []
    for job in jobs:
        job_info = jobpostserializer(job, context={'request': request}).data
        job_info['time_ago_posted'] = timesince(job.Posted_Date) + " ago"  # Calculate the time since Posted_Date
        job_data.append(job_info)
    
    return Response(job_data)

@api_view(['POST'])
def Saved_job(request,id):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=get_object_or_404(Userinfo,Email=current_user)
    else:
        return Response({'msg':'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    try:
        # Check if the job is already saved by the user
        job_posting = get_object_or_404(JobPostings, id=id)
        if Saved_Jobs.objects.filter(User=user, Saved_job=job_posting).exists():
            return Response({'msg': 'Job already saved'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the job for the user
        Saved_Jobs.objects.create(User=user, Saved_job=job_posting)
        return Response({'msg': 'Saved successfully'}, status=status.HTTP_201_CREATED)
    
    except IntegrityError:
        return Response({'msg': 'Integrity error occurred'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'msg': 'Something went wrong', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def Display_Saved_Jobs(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=get_object_or_404(Userinfo,Email=current_user)
    else:
        return Response({'msg':'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    saved_jobs = Saved_Jobs.objects.filter(User=user).select_related('Saved_job')

    # Get the related JobPostings from Saved_Jobs
    job_postings = [saved_job.Saved_job for saved_job in saved_jobs]

    # Serialize the job postings
    serializer = jobpostserializer(job_postings, many=True, context={'request': request})

    return Response(serializer.data)
    
    
    
@api_view(['POST'])
def search_by_jobtitle(request):
    if request.method == 'POST':
        search = request.data.get('Search', None)  # Use .get() to avoid KeyError
        
        if not search:
            return Response({'msg': 'Search term is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform a case-insensitive search using __icontains
        result = JobPostings.objects.filter(Jobtitle__icontains=search)
        
        if result.exists():
            serializer = jobpostserializer(result, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'No Jobs in this title. Stay Updated.'}, status=status.HTTP_404_NOT_FOUND)
        
        
@api_view(['GET'])
def Display_Job_Posted(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=get_object_or_404(Userinfo,Email=current_user)
    else:
        return Response({'msg':'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    job_posted_by_me=JobPostings.objects.filter(User=user.id)
    print(f'User ID: {user.id}, Posted Jobs: {job_posted_by_me.count()}')

    if job_posted_by_me.exists():
        serializer = jobpostserializer(job_posted_by_me, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'msg': 'No Jobs Posted Yet!'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def Filteration(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)

    job_category = request.data.get('Category')
    job_type = request.data.get('Type')
    experience = request.data.get('Experience')
    location = request.data.get('Location')
    min_salary = request.data.get('Min_salary')

    filter_params = {}
    if job_category:
        filter_params['Job_Category'] = job_category
    if job_type:
        filter_params['Job_Type'] = job_type
    if experience:
        filter_params['Jobexperience'] = experience
    if location:
        filter_params['District'] = location
    if min_salary:
        filter_params['Min_salary__gte'] = min_salary  

    result = JobPostings.objects.filter(**filter_params)

    if result.exists():
        serializer = jobpostserializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'msg': 'No Jobs!'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def create_profile(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    request.data['User']=user.id
    serializer = ProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def Show_profile(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    profile=Profile.objects.filter(User=user.id)
    if profile.exists():
        serializer=ProfileSerializer(profile,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'msg': 'Profile unavailable!'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def apply_job(request, id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    try:
        applicant_profile = get_object_or_404(Profile, User=user)
    except Profile.DoesNotExist:
        return Response({'msg':'Please Create user Profile first!'})
    posted_by = get_object_or_404(JobPostings, id=id)

    application_data = {
        'Applicant': user.id,
        'Applicant_profile': applicant_profile.id,
        'Posted_by': posted_by.id,
        'RelevantSkill': request.data.get('RelevantSkill'),  
        'Portfolio_link': request.data.get('Portfolio_link'),
        'Cover_letter': request.data.get('Cover_letter'),
        'Resume': request.data.get('Resume'),
    }

    application_serializer = applyserializer(data=application_data)

    if application_serializer.is_valid():  
        application_serializer.save()  
        return Response({'msg': 'Successfully Applied!'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'msg': 'Something went wrong in application!', 'errors': application_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
def received_application(request):
    # Check if the user is authenticated
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)

    # Get the job postings created by the user
    posted_by = JobPostings.objects.filter(User=user).first()
    if not posted_by:
        return Response({'msg': 'No job postings found for this user'}, status=status.HTTP_404_NOT_FOUND)

    # Get applications received for the job posting
    application_receive = Applications_received.objects.filter(Posted_by=posted_by)
    
    # Prepare the response data
    applications = []
    for application in application_receive:
        applications.append({
            'id': application.id,  # Include the ID for later reference
            'applicant_name': application.Applicant_profile.User_Name,
            'applicant_img': application.Applicant_profile.User_Photo.url if application.Applicant_profile.User_Photo else None,
            'applicant_title': application.Applicant_profile.Title,
            'applicant_qualification': application.Applicant_profile.Qualification,
        })

    return Response({'applications': applications}, status=status.HTTP_200_OK)

@api_view(['GET'])
def application_detail(request,id):
    # Check if the user is authenticated
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)

    # Get the specific application by ID
    application = get_object_or_404(Applications_received, id=id)

    # Prepare the response data for the specific application
    application_detail = {
        'applicant_name': application.Applicant_profile.User_Name,
        'applicant_img': application.Applicant_profile.User_Photo.url if application.Applicant_profile.User_Photo else None,
        'applicant_title': application.Applicant_profile.Title,
        'applicant_qualification': application.Applicant_profile.Qualification,
        'relevant_skill': application.RelevantSkill,
        'portfolio_link': application.Portfolio_link,
        'cover_letter': application.Cover_letter.url if application.Cover_letter else None,
        'resume': application.Resume.url if application.Resume else None,
    }

    return Response(application_detail, status=status.HTTP_200_OK)
                
                
@api_view(['GET'])
def applied_jobs(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    
    jobs=Applications_received.objects.filter(Applicant=user.id)
    
    applied_job_list=[]
    for job in jobs:
        applied_job_list.append({
            'Hiring By':job.Posted_by.User.Username,
            'Company':job.Posted_by.Company_name,
            'Job Role':job.Posted_by.Jobtitle,
            'Category':job.Posted_by.Job_Category,
            'Applied_date':job.Applied_date
        })
    return Response({'applied_jobs':applied_job_list})
        
           

@api_view(['GET'])
def recommeded_jobs(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    user_profile=Profile.objects.filter(User=user.id).first()
    if user_profile is None:
        return Response({'msg': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    job_title = user_profile.Title
    job_title=user_profile.Title
    recommends=JobPostings.objects.filter(Job_Category=job_title)
    if recommends.exists():
        serializer=jobpostserializer(recommends,many=True)
        return Response(serializer.data)
    else:
        return Response({'msg':'No recommended jobs yet!'})
    
@api_view(['DELETE'])
def deletejobposting(request,id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    
    posted_jobs=JobPostings.objects.filter(id=id,User=user.id).first()
    if posted_jobs:
        posted_jobs.delete()
        return Response({'msg':'Job list Deleted!'})
    else:
        return Response({'msg':'Something went wrong!'})



@api_view(['PUT'])
def Editjobpost(request,id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    posted_job=JobPostings.objects.filter(User=user,id=id).first()
    if not posted_job:
        return Response({'msg': 'Job post not found or unauthorized access'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = jobpostserializer(posted_job, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({'msg': 'Job post updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)