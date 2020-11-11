from django.shortcuts import render,redirect
import pyrebase
from django.contrib.auth import logout

firebaseConfig = {
  'apiKey': "AIzaSyA9lWECICW_Tbj4lahpB0VuzmjlGaLnnXo",
  'authDomain': "login-demo-148c2.firebaseapp.com",
  'databaseURL': "https://login-demo-148c2.firebaseio.com",
  'projectId': "login-demo-148c2",
  'storageBucket': "login-demo-148c2.appspot.com",
  'messagingSenderId': "900718925900",
  'appId': "1:900718925900:web:d74a97a3eacbc3efa77ce9",
  'measurementId': "G-CE0QD1888L"
};

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
database = firebase.database()
def signIn(request):
    return render(request,"signIn.html")

def postsign(request):
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    try:
        user = auth.sign_in_with_email_and_password(email,passw)
    except:
        message = "Invalid Credentials"
        return render(request,'signIn.html',{'messg':message})
    print(user['idToken'])
    session_id = user['idToken']
    request.session['uid']=str(session_id) 
    uid= user['localId']
    data = {'email':email,"status":"logged"}
    database.child("users").child(uid).child("details").set(data) 
    return render(request,'welcome.html',{"e":email})

def loggedout(request):
    logout(request)
    return redirect('/')





