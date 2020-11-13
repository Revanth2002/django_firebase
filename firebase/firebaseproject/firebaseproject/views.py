from django.shortcuts import render,redirect
import pyrebase
from django.contrib.auth import logout
import time
from datetime import timezone
import datetime 
import pytz

firebaseConfig = {
  'apiKey': "APIKEY",
  'authDomain': "AUTHDOMAIN",
  'databaseURL': "DATABSEURL",
  'projectId': "PROJECTURL",
  'storageBucket': "STORAGEBUCKET",
  'messagingSenderId': "MESSAGESENDERID",
  'appId': "APPID",
  'measurementId': "MEASUREMENTID"
};

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
database = firebase.database()

def signIn(request):
    return render(request,"signIn.html")

def postsign(request):
    import re
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    regex_1 = re.compile("(?:@|^)[^@]*")
    reg = regex_1.findall(email)
    name = reg[0]
    try:
        user = auth.sign_in_with_email_and_password(email,passw)
    except:
        message = "Invalid Credentials"
        return render(request,'signIn.html',{'messg':message})
    print(user['idToken'])
    session_id = user['idToken']
    request.session['uid']=str(session_id) 

    
    uid= user['localId']
    data = {'name': name ,'email':email,"status":"logged"}
    database.child("users").child(uid).child("details").set(data) 
    return render(request,'welcome.html',{"e":email})

def loggedout(request):
    logout(request)
    return redirect('/')


def signUp(request):
    return render(request,'signup.html')

def postsignup(request):
    if request.method=='post':
        name = request.POST.get('name')   
        email = request.POST.get('email')
        passw = request.POST.get('pass')
        try:
            user = auth.create_user_with_email_and_password(email,passw)
            return redirect('/')
        except:
            message = "Unable to create account,Try again"
            return render(request,'signIn.html',{"messg":message})
            uid = user['localId']
            
        data ={"name":name,"status":"1"}
        firebase.child("users").child(uid).child("details").set(data)
        return render(request,"signIn.html")

def create(request):

    return render(request,'create.html')


def post_create(request):


    tz=pytz.timezone('Asia/Kolkata')
    time_now = datetime.datetime.now(timezone.utc).astimezone(tz)
    millis = int(time.mktime(time_now.timetuple()))
    work = request.POST.get('work')
    progress = request.POST.get('progress')

    idtoken = request.session['uid']
    a = auth.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    data = {
    
        'work':work,
        "progress":progress  
    }
    database.child('users').child(a).child('reports').child(millis).set(data)
    name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request,'welcome.html',{"e":name})

def check(request):
    idtoken = request.session['uid']
    a = auth.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']    

    timestamp= database.child('users').child(a).child('reports').shallow().get().val()
    lis_time=[]
    for i in timestamp:
        lis_time.append(i)
    lis_time.sort(reverse = True)  
    #print(lis_time)
    work=[]
    for i in lis_time:
        wor=database.child('users').child(a).child('reports').child(i).child('work').get().val()
        work.append(wor)  
    #print(work)
    date=[]
    for i in lis_time:
        i = float(i)
        dat= datetime.datetime.fromtimestamp(i).strftime("%H:%M %d-%m-%Y")
        date.append(dat)  
    #print(date)    
    name = database.child('users').child(a).child('details').child('name').get().val()
    comb_lis=[]
    
    for a,b,c in zip(lis_time,date,work):
        d = a,b,c
        comb_lis.append(d)
        #print(c)     
    print(comb_lis)
    return render(request,'check.html',{'comb_lis':comb_lis,'e': name})
  
def post_check(request):
    time = request.GET.get('z')

    idtoken = request.session['uid']
    a = auth.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']    

    work = database.child("user").child(a).child('reports').child(time).child('work').get().val()
    progress = database.child("user").child(a).child('reports').child(time).child('progress').get().val()
    i=float(time)
    dat= datetime.datetime.fromtimestamp(i).strftime("%H:%M %d-%m-%Y")
    name = database.child('users').child(a).child('details').child('name').get().val()
   
    return render(request,'post_check.html',{'w':work,'p':progress,'d':dat,'e':name})   
    
