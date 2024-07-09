from django.urls import path
from authentication import views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/',views.LoginView.as_view(),name="LoginView"),
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/changepassword/',views.UserChangePassword.as_view(),name="changepassword"),
    path("sent_reset_password_email/",views.ResetPasswordEmailRequest.as_view(),name="ResetPasswordEmailRequest"),
    path("reset_password/<uid>/<token>/",views.UserPasswordResetView.as_view(),name="ResetPasswordView"),
    path("profile/",views.ProfileGetUpdateView.as_view(),name="ProfileGetUpdateView"),
    path("profile/change_password/",views.UserChangePassword.as_view(),name="ProfileGetUpdateView"),
    path("user/",views.UserListCreateView.as_view(),name="UserListCreateView"),
    path('user/<int:pk>/',views.UserUpdateDeleteView.as_view(),name="UserUpdateDeleteView"),

]