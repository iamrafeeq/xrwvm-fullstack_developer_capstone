from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views  # Make sure views.py has the login_user view
from .views import registration

app_name = 'djangoapp'

urlpatterns = [
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path("register", registration, name="register"),  


    # Add other paths here, for example:
    # path('register', views.register_user, name='register'),
    # path('reviews', views.dealer_reviews, name='reviews'),
    # path('add_review', views.add_review, name='add_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
