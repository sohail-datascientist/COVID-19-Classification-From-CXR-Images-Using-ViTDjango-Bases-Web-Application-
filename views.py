import os
import cv2
import time
from PIL import Image
import numpy as np
import glob
import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot as plt
from django.shortcuts import render
from keras.models import model_from_json
from keras.preprocessing import image
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
import mysql.connector as sql
import requests
from sqlalchemy import false
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth

# Create your views here.

covid_pred = ['Covid-19', 'Non Covid-19']
IMAGE_SIZE = 64

vit_model = 'predictor/model_weights/ViT/Vit.h5'
vit_json = 'predictor/model_weights/ViT/Vit_Model.json'
xception_model = 'predictor/model_weights/Xception/Xception_Model.h5'
xception_json = 'predictor/model_weights/Xception/Xception_Model.json'


def read_image(filepath):
    return cv2.imread(filepath) 

def resize_image(image, image_size):
    return cv2.resize(image.copy(), image_size, interpolation=cv2.INTER_AREA)


def clear_mediadir():
    media_dir = "./media"
    for f in os.listdir(media_dir):
        os.remove(os.path.join(media_dir, f))



def home(request):
    return render(request, 'index.html')


    
def index(request):
    if request.method == "POST" :
        clear_mediadir() 

        img = request.FILES['ImgFile']
        fs = FileSystemStorage()
        filename = fs.save(img.name, img)
        img_path = fs.path(filename)

        pred_arr = np.zeros(
            (1, IMAGE_SIZE, IMAGE_SIZE, 3))

        im = read_image(img_path)
        #im = np.array(im)
        r,g,b=cv2.split(im)

        #spliting b,g,r and getting differences between them
        r_g=np.count_nonzero(abs(r-g))
        r_b=np.count_nonzero(abs(r-b))
        g_b=np.count_nonzero(abs(g-b))

        diff_sum=float(r_g+r_b+g_b)
        #finding ratio of diff_sum with respect to size of image
        ratio=diff_sum/img.size
        
        if ratio<0.005:
            if im is not None:
                pred_arr[0] = resize_image(im, (IMAGE_SIZE, IMAGE_SIZE))
            pred_arr = pred_arr/255


            vit_start = time.time()
            with open(vit_json, 'r') as vitjson:
                vitmodel = model_from_json(vitjson.read())

            vitmodel.load_weights(vit_model)
            label_vit = vitmodel.predict(pred_arr)
            idx_vit = np.argmax(label_vit[0])
            cf_score_vit = np.amax(label_vit[0])
            vit_end = time.time()

            vit_exec = vit_end - vit_start

            xception_start = time.time()
            with open(xception_json, 'r') as xceptionjson:
                xceptionmodel = model_from_json(xceptionjson.read())

            xceptionmodel.load_weights(xception_model)
            label_xception = xceptionmodel.predict(pred_arr)
            idx_xception = np.argmax(label_xception[0])
            cf_score_xception = np.amax(label_xception[0])
            xception_end = time.time()

            xception_exec = xception_end - xception_start

            print('Prediction (ViT): ', covid_pred[idx_vit])
            print('Confidence Score (ViT) : ',cf_score_vit)
            print('Prediction Time (ViT) : ', vit_exec)
            print("\n")
            print('Prediction (Xception): ', covid_pred[idx_xception])
            print('Confidence Score (Xception) : ', cf_score_xception)
            print('Prediction Time (Xception) : ', xception_exec)
            print("\n")
            print(img_path)

            response = {}
            response['table'] = "table"
            response['col0'] = " "
            response['col2'] = "ViT"
            response['col3'] = "Xception"
            response['row1'] = "Results"
            response['row2'] = "Confidence Score"
            response['row3'] = "Prediction Time (s)"
            response['r_pred'] = covid_pred[idx_vit]
            response['x_pred'] = covid_pred[idx_xception]
            response['r_cf'] = cf_score_vit
            response['x_cf'] = cf_score_xception 
            response['r_time'] = vit_exec
            response['x_time'] = xception_exec 
            response['image'] = "../media/" + img.name
            return render(request, 'index1.html', response)
        else:
            return render(request, 'error.html')
    else:
        return render(request, 'index1.html')




# Create your views here.
def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is already taken')
                return redirect(register)
            else:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                user.save()
                return render(request, 'index1.html')
        else:
            messages.info(request, 'Both passwords are not matching')
            return render(request, 'signup_page.html')  
    else:
        return render(request, 'signup_page.html')




def dashboard(request): 
    data = True
    result = None
    globalSummary = None
    countries = None


    while(data):
        try:
            #return HttpResponse("My Application")
            result = requests.get('https://api.covid19api.com/summary')
            globalSummary = result.json()['Global']
            countries = result.json()['Countries']
            data = False
        except:
            data = True
        
        lables =[]
        chartdata = []

        for state in countries:
            lables.append(state['Country'])
            chartdata.append(state['TotalDeaths'])

    return render (request, 'indexx.html', 
                                    {'globalSummary': globalSummary,
                                    'countries':countries,
                                    'lables':lables,
                                    'chartdata':chartdata})

# em=''
# pwd=''
# # Create your views here.
# def login_user(request):
#     global em,pwd

#     data = True
#     result = None
#     globalSummary = None
#     countries = None


#     while(data):
#         try:
#             #return HttpResponse("My Application")
#             result = requests.get('https://api.covid19api.com/summary')
#             globalSummary = result.json()['Global']
#             countries = result.json()['Countries']
#             data = False
#         except:
#             data = True
        
#         lables =[]
#         chartdata = []

#         for state in countries:
#             lables.append(state['Country'])
#             chartdata.append(state['TotalDeaths'])


#     if request.method=="POST":
#         m=sql.connect(host="localhost",user="root",passwd="1234",database='website')
#         cursor=m.cursor()
#         d=request.POST
#         for key,value in d.items():
#             if key=="email":
#                 em=value
#             if key=="password":
#                 pwd=value
        
#         c="select * from users where email='{}' and password='{}'".format(em,pwd)
#         cursor.execute(c)
#         t=tuple(cursor.fetchall())
#         if t==():
#             return render(request,'error.html')
#         else:
            
#             return render (request, 'indexx.html', 
#                                     {'globalSummary': globalSummary,
#                                     'countries':countries,
#                                     'lables':lables,
#                                     'chartdata':chartdata})


#     return render(request,'login_page.html')

def login_user(request):
   
    data = True
    result = None
    globalSummary = None
    countries = None


    while(data):
        try:
            #return HttpResponse("My Application")
            result = requests.get('https://api.covid19api.com/summary')
            globalSummary = result.json()['Global']
            countries = result.json()['Countries']
            data = False
        except:
            data = True
        
        lables =[]
        chartdata = []

        for state in countries:
            lables.append(state['Country'])
            chartdata.append(state['TotalDeaths'])

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return render (request, 'indexx.html', 
                                    {'globalSummary': globalSummary,
                                    'countries':countries,
                                    'lables':lables,
                                    'chartdata':chartdata})
        else:
            messages.info(request, 'Invalid Username or Password')
            return render(request, 'login_page.html')



    else:
        return render(request, 'login_page.html')



def logout_user(request):
    auth.logout(request)
    return render(request, 'index.html')