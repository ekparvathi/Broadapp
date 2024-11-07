from django.urls import path
from doctorSection import views as docSectionView
urlpatterns=[ 
   
    path('getDoctorsN/', docSectionView.getDoctorsN, name='getDoctorsN'),
    path('getDoctorsS/<int:id>', docSectionView.getDoctorsS, name='getDoctorsS'),
    path('getDoctorsH/<int:id>', docSectionView.getDoctorsH, name='getDoctorsH'),
    path('getDoctorsAll/', docSectionView.getDoctorsAll, name='getDoctorsAll'),
    path('getSpecializeAll/', docSectionView.getSpecializeAll, name='getSpecializeAll'),
    path('getHospitalAll/', docSectionView.getHospitalAll, name='getHospitalAll'),
    path('getHospitalsNear/', docSectionView.getHospitalsNear, name='getHospitalsNear'),
    path('getDoctorsNear/', docSectionView.getDoctorsNear, name='getDoctorsNear'),
    path('makeAppoint/', docSectionView.makeAppoint, name='makeAppoint'),
    path('getAppointmentDetail/<int:id>', docSectionView.getAppointmentDetail, name='getAppointmentDetail'),
    path('getAllAppointments/', docSectionView.getAllAppointments, name='getAllAppointments'),
    path('getAvailableTimeSlots/<int:id>', docSectionView.getAvailableTimeSlots, name='getAvailableTimeSlots'), 
    path('getBookedTimeSlots/<int:id>', docSectionView.getBookedTimeSlots, name='getBookedTimeSlots'), 
    path('setAppointmentReminder/<int:id>', docSectionView.setAppointmentReminder, name='setAppointmentReminder'),
    path('searchDoctorByNameAndSpecialization/',docSectionView.searchDoctorByNameAndSpecialization,name='searchDoctorByNameAndSpecialization'),
    path('searchDoctorByNameAndHospital/',docSectionView.searchDoctorByNameAndHospital,name='searchDoctorByNameAndHospital'),
    path('getDoctorsBySpecialization/',docSectionView.getDoctorsBySpecialization,name='getDoctorsBySpecialization'),
    path('getDoctorsByHospital/',docSectionView.getDoctorsByHospital,name='getDoctorsByHospital'),
    path('search_Doctor_Hospital/',docSectionView.search_Doctor_Hospital,name='search_Doctor_Hospital'),
]

