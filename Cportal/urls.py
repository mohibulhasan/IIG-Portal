from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    
    path('', views.home, name='home'),
    path('user/', views.userPage, name="user-page"),
    path("contact", views.contact, name="contact"),
    
    path('routestat', views.bgplay, name='routestat'),
    path('routetroubleshoot', views.route_troubleshoot_customer, name='routetroubleshoot'),
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),),

    path('emailinfo', views.create_emailadd_view, name='emailinfo'),
    path('emailupdateinfo/<str:pk>', views.update_email_view, name='emailupdateinfo'),
    path('deleteemailinfo/<str:pk>', views.delete_email_view, name='deleteemailinfo'),

    path('phoneinfo', views.create_phoneadd_view, name='phoneinfo'),
    path('phoneupdateinfo/<str:pk>', views.update_phone_view, name='phoneupdateinfo'),
    path('deletephoneinfo/<str:pk>', views.delete_phone_view, name='deletephoneinfo'),

    path('userinfo', views.create_userinfo_view, name='userinfo'),
    path('userupdateinfo/<str:pk>', views.update_userinfo_view, name='userupdateinfo'),
    path('deleteuserinfo/<str:pk>', views.delete_userinfo_view, name='deleteuserinfo'),

    path('customerprofile', views.customer_profile_view, name='customerprofile'),
    path('intstatus', views.customer_graph_view, name='intstatus'),

    path('customerinfo', views.create_customerinfo_view, name='customerinfo'),
    path('customerupdateinfo/<str:pk>', views.update_customerinfo_view, name='customerupdateinfo'),
    path('deletecustomerinfo/<str:pk>', views.delete_customerinfo_view, name='deletecustomerinfo'),

    path('customerproperties', views.create_customerproperties_view, name='customerproperties'),
    path('customerpropertiesupdate/<str:pk>', views.update_customerproperties_view, name='customerpropertiesupdate'),
    path('deletecustproperties/<str:pk>', views.delete_deletecustproperties_view, name='deletecustproperties'),
    
    path('locationinfo', views.create_location_view, name='locationinfo'),
    path('locationupdate/<str:pk>', views.update_location_view, name='locationupdate'),
    path('deletelocation/<str:pk>', views.delete_location_view, name='deletelocation'),

    path('deviceinfo', views.device_add_view, name='deviceinfo'),
    path('deviceupdate/<str:pk>', views.device_update_view, name='deviceupdate'),
    path('deletedevice/<str:pk>', views.delete_device_view, name='deletedevice'),

    path('interfaceinfo', views.Interface_add_view, name='interfaceinfo'),
    path('interfaceupdate/<str:pk>', views.Interface_update_view, name='interfaceupdate'),
    path('deleteinterface/<str:pk>', views.delete_interface_view, name='deleteinterface'),

    path('devices', views.device_view, name='devices'),
    path('interfaces', views.interface_view, name='interfaces'),
    path('BSCCL-DHK-CORE-01', views.dhk_core_01_view, name='BSCCL-DHK-CORE-01'),
    path('BSCCL-DHK-AGG-01', views.DHK_AGG_01_view, name='BSCCL-DHK-AGG-01'),
    path('BSCCL-COX-CORE-01', views.COX_CORE_01_view, name='BSCCL-COX-CORE-01'),
    path('BSCCL-COX-CORE-02', views.COX_CORE_02_view, name='BSCCL-COX-CORE-02'),
    path('BSCCL-KKT-CORE-RTR-01', views.KKT_CORE_01_view, name='BSCCL-KKT-CORE-RTR-01'),
    path('BSCCL-KKT-CORE-RTR-02', views.KKT_CORE_02_view, name='BSCCL-KKT-CORE-RTR-02'),
    path('BSCCL-CORE-NEXUS-SW', views.nexus_sw_01_view, name='BSCCL-CORE-NEXUS-SW'),
    path('BSCCL-AGG-NEXUS-SW', views.nexus_sw_02_view, name='BSCCL-AGG-NEXUS-SW'),
    path('BSCCL-NRB-POP', views.nexus_NRB_view, name='BSCCL-NRB-POP'),
    path('BSCCL-ACCESS-SW-01', views.access_sw_01_view, name='BSCCL-ACCESS-SW-01'),
    path('BSCCL-CTG-SW-01', views.access_sw_CTG_view, name='BSCCL-CTG-SW-01'),
    path('BSCCL-COX-NEXUS-01', views.nexus_cox_01_view, name='BSCCL-COX-NEXUS-01'),

    path('customers', views.customer_view, name='customers'),  
    path('clientdetails/<str:pk>', views.clientdetails_view, name='clientdetails'),  
    path('alert/', csrf_exempt(views.alertapi_view)),

    path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name="Cportal/Loginpass/password_reset.html"),
     name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="Cportal/Loginpass/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="Cportal/Loginpass/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="Cportal/Loginpass/password_reset_done.html"), 
        name="password_reset_complete"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)