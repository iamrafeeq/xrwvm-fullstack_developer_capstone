


from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import logging
import json

from .models import CarMake, CarModel
from .populate import initiate
# from .restapis import get_request, analyze_review_sentiments, post_review
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)

# =========================
# LOGIN VIEW
# =========================
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)
    data = {"userName": username}

    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}

    return JsonResponse(data)


# =========================
# LOGOUT VIEW
# =========================
def logout_user(request):
    logout(request)
    return JsonResponse({"userName": ""})


# =========================
# REGISTRATION VIEW
# =========================
@csrf_exempt
def registration(request):
    data = json.loads(request.body)

    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    try:
        User.objects.get(username=username)
        return JsonResponse({"userName": username, "error": "Already Registered"})
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})


# =========================
# GET CARS
# =========================
def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = []

    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    return JsonResponse({"CarModels": cars})


# =========================
# GET DEALERSHIPS
# =========================
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})



# =========================
# GET DEALER DETAILS
# =========================
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealer = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealer})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})



# =========================
# GET DEALER REVIEWS
# =========================
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)

        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            review_detail['sentiment'] = response.get('sentiment', 'neutral')

        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})



# =========================
# ADD REVIEW
# =========================
# @csrf_exempt
# def add_review(request):
#     if not request.user.is_anonymous:
#         data = json.loads(request.body)
#         try:
#             post_review(data)
#             return JsonResponse({"status": 200})
#         except:
#             return JsonResponse({"status": 401, "message": "Error posting review"})
#     else:
#         return JsonResponse({"status": 403, "message": "Unauthorized"})


def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
