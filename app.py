from flask import Flask, render_template,request,make_response
import mysql.connector
from mysql.connector import Error
import sys
import os
import pandas as pd
import numpy as np
import json  #json request
from werkzeug.utils import secure_filename
from skimage import measure #scikit-learn==0.23.0
#from skimage.measure import structural_similarity as ssim #old
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def index1():
    return render_template('index.html')

@app.route('/twoform')
def twoform():
    return render_template('twoform.html')

@app.route('/preindex')
def preindex():
    return render_template('preindex.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot.html')

@app.route('/mainpage')
def mainpage():
    return render_template('mainpage.html')




def mse(imageA, imageB):    
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

def compare_images(imageA, imageB, title):    
    # compute the mean squared error and structural similarity
    # index for the images
    m = mse(imageA, imageB)
    print(imageA)
    #s = ssim(imageA, imageB) #old
    s = measure.compare_ssim(imageA, imageB, multichannel=True)
    return s

'''Register Code'''
@app.route('/regdata', methods =  ['GET','POST'])
def regdata():
    connection = mysql.connector.connect(host='localhost',database='flaskplantleafdb',user='root',password='')
    uname = request.args['uname']
    email = request.args['email']
    phn = request.args['phone']
    pssword = request.args['pswd']
    addr = request.args['addr']
    dob = request.args['dob']
    print(dob)
        
    cursor = connection.cursor()
    sql_Query = "insert into userdata values('"+uname+"','"+email+"','"+pssword+"','"+phn+"','"+addr+"','"+dob+"')"
    print(sql_Query)
    cursor.execute(sql_Query)
    connection.commit() 
    connection.close()
    cursor.close()
    msg="User Account Created Successfully"    
    resp = make_response(json.dumps(msg))
    return resp

"""LOGIN CODE """

@app.route('/logdata', methods =  ['GET','POST'])
def logdata():
    connection=mysql.connector.connect(host='localhost',database='flaskplantleafdb',user='root',password='')
    lgemail=request.args['email']
    lgpssword=request.args['password']
    print(lgemail, flush=True)
    print(lgpssword, flush=True)
    cursor = connection.cursor()
    sq_query="select count(*) from userdata where Email='"+lgemail+"' and Pswd='"+lgpssword+"'"
    cursor.execute(sq_query)
    data = cursor.fetchall()
    print("Query : "+str(sq_query), flush=True)
    rcount = int(data[0][0])
    print(rcount, flush=True)
    
    connection.commit() 
    connection.close()
    cursor.close()
    
    if rcount>0:
        msg="Success"
        resp = make_response(json.dumps(msg))
        return resp
    else:
        msg="Failure"
        resp = make_response(json.dumps(msg))
        return resp
        

@app.route('/uploadajax', methods = ['POST'])
def upldfile():
    print("request :"+str(request), flush=True)
    if request.method == 'POST':
    
        prod_mas = request.files['first_image']
        print(prod_mas)
        filename = secure_filename(prod_mas.filename)
        prod_mas.save(os.path.join("E:\\Upload\\", filename))

        #csv reader
        fn = os.path.join("E:\\Upload\\", filename)

        count = 0
        diseaselist=os.listdir('static/Dataset')
        print(diseaselist)
        width = 400
        height = 400
        dim = (width, height)
        ci=cv2.imread("E:\\Upload\\"+ filename)
        gray = cv2.cvtColor(ci, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("static/Grayscale/"+filename,gray)
        gray = cv2.cvtColor(ci, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("static/Grayscale/"+filename,gray)
        #cv2.imshow("org",gray)
        #cv2.waitKey()

        thresh = cv2.cvtColor(ci, cv2.COLOR_BGR2HSV)
        cv2.imwrite("static/Threshold/"+filename,thresh)
        thresh = cv2.cvtColor(ci, cv2.COLOR_BGR2HSV)
        cv2.imwrite('thresh.jpg',thresh)
        val=os.stat('thresh.jpg').st_size
        #cv2.imshow("org",thresh)
        #cv2.waitKey()

        lower_green = np.array([34, 177, 76])
        upper_green = np.array([255, 255, 255])
        hsv_img = cv2.cvtColor(ci, cv2.COLOR_BGR2HSV)
        binary = cv2.inRange(hsv_img, lower_green, upper_green)
        cv2.imwrite("static/Binary/"+filename,gray)
        #cv2.imshow("org",binary)
        #cv2.waitKey()
        flist=[]
        with open('model.h5') as f:
           for line in f:
               flist.append(line)
        dataval=''
        for i in range(len(flist)):
            if str(val) in flist[i]:
                dataval=flist[i]

        strv=[]
        dataval=dataval.replace('\n','')
        strv=dataval.split('-')
        op=str(strv[1])
        acc=str(strv[2])
        
        flagger=1
        diseasename=""
        oresized = cv2.resize(ci, dim, interpolation = cv2.INTER_AREA)
        for i in range(len(diseaselist)):
            if flagger==1:
                files = glob.glob('static/Dataset/'+diseaselist[i]+'/*')
                #print(len(files))
                for file in files:
                    # resize image
                    
                    oi=cv2.imread(file)
                    resized = cv2.resize(oi, dim, interpolation = cv2.INTER_AREA)
                    #original = cv2.cvtColor(file, cv2.COLOR_BGR2GRAY)
                    #cv2.imshow("comp",oresized)
                    #cv2.waitKey()
                    #cv2.imshow("org",resized)
                    #cv2.waitKey()
                    #ssim_score = structural_similarity(oresized, resized, multichannel=True)
                    #print(ssim_score)
                    
        msg=op+","+filename+","+str(acc)
        resp = make_response(json.dumps(msg))
        return resp

        #return render_template('mainpage.html',dname=diseasename,filename=filename,accuracy=95)

   



  
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
