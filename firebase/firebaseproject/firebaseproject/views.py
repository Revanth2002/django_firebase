from django.shortcuts import render,redirect
import pyrebase
from django.contrib.auth import logout
import time
from datetime import timezone
import datetime 
import pytz 
from django.http import HttpResponse
from firebase import firebase


firebaseConfig = {
  'apiKey': "--API-KEY--",
  'authDomain': "--YOUR DOMAIN--",
  'databaseURL': "--DATABASE-URL--",
  'projectId': "--PROJECT-ID--",
  'storageBucket': "--STORAGE-BUCKET--",
  'messagingSenderId': "--MSG_ID--",
  'appId': "--APP_ID--",
  'measurementId': "--MEASUREMENT_ID--"
};
firebase1 = firebase.FirebaseApplication('https://login-demo-148c2.firebaseio.com/users',None)

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
    except Exception:
        message = "Invalid Credentials"
        return render(request,'signIn.html',{'messg':message})
    #print(user['idToken'])
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
        
        name = request.POST.get('name')   
        email = request.POST.get('email')
        passw = request.POST.get('pass')
        try:
            user = auth.create_user_with_email_and_password(email,passw)
            
        except Exception:
            message = "Unable to create account,Try again"
            return render(request,'signup.html',{"messg":message})
            uid = user['localId']
            print(Exception) 
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
    url = request.POST.get('url')

    idtoken = request.session['uid']
    a = auth.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    data = {
        'work':work,
        "progress":progress ,
        "url":url 
    }
    database.child('users').child(a).child('reports').child(millis).set(data)
    name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request,'welcome.html',{"e":name})

def check(request):
    date_cons="%H:%M %d-%m-%Y"
    if request.method =='GET' and 'csrfmiddlewaretoken' in request.GET:
        search = request.GET.get('search')
        search = search.lower()
        
        idtoken = request.session['uid']
        a = auth.get_account_info(idtoken)
        a = a['users']
        a = a[0]
        uid = a['localId']
        #print(uid)   

        timestamp= database.child('users').child(uid).child('reports').shallow().get().val()
        #print(timestamp) 
        work_id=[]
        for i in timestamp: 
            ref = database.child('users').child(uid).child('reports').child(i).child('work').get().val()
            ref = str(ref)+"$"+str(i)
            work_id.append(ref)
        #print(work_id)    
        matching=[str(string) for string in work_id if search in string.lower() ]
        
        s_work = []    
        s_id=[]
        for j in matching:
            work,ids=j.split("$")
            s_work.append(work)
            s_id.append(ids)

        date=[]
        for i in s_id:
            i = float(i)
            dat= datetime.datetime.fromtimestamp(i).strftime(date_cons)
            date.append(dat)  
        #print(date)    
        name = database.child('users').child(uid).child('details').child('name').get().val()
        comb_lis=[]
        for a,b,c in zip(s_id,date,s_work):
            d = a,b,c
            comb_lis.append(d)
            
        #print(comb_lis)
        return render(request,'check.html',{'comb_lis':comb_lis,'e': name,'uid':uid})

        
    else:
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
            dat= datetime.datetime.fromtimestamp(i).strftime(date_cons)
            date.append(dat)  
        #print(date)    
        name = database.child('users').child(a).child('details').child('name').get().val()
        comb_lis=[]
        
        for a,b,c in zip(lis_time,date,work):
            d = a,b,c
            comb_lis.append(d)
            
        #print(comb_lis)
        return render(request,'check.html',{'comb_lis':comb_lis,'e': name,'uid':a})


timex = 0
def post_check(request):
    
    global timex
    timex = request.GET.get('z')
    
    idtoken = request.session['uid']
    a = auth.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']  

    i=float(timex)
    dat= datetime.datetime.fromtimestamp(i).strftime("%H:%M %d-%m-%Y")
    
    ref = database.child('users').child(a).child('reports').child(timex).child('work').get().val()
    ref1 = database.child('users').child(a).child('reports').child(timex).child('progress').get().val()
    ref2 = database.child('users').child(a).child('reports').child(timex).child('url').get().val()
    #print(time)
    #print(ref)
    #print(ref1)
    #print(ref2)
    
    name = database.child('users').child(a).child('details').child('name').get().val()
   
    return render(request,'post_check.html',{'w':ref,'p':ref1,'d':dat,'e':name,'i':ref2})   
    
def back(request):
    return redirect('check')

    
def delete(request):
    
    idtoken = request.session['uid']
    a = auth.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId'] 
    delete = database.child('users').child(a).child('reports').child(timex).remove()
    
    print(timex)
    return redirect('check') 

def update(request):
    idtoken = request.session['uid']
    a = auth.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']  

    i=float(timex)
    dat= datetime.datetime.fromtimestamp(i).strftime("%H:%M %d-%m-%Y")
    
    firebase1.put('/users/Mb69anRZVeeMfHAUjZKxfxRvunk1/reports/1605247316','work','Succesfull')
    ref = database.child('users').child(a).child('reports').child(timex).child('work').get().val()
    ref1 = database.child('users').child(a).child('reports').child(timex).child('progress').get().val()
    ref2 = database.child('users').child(a).child('reports').child(timex).child('url').get().val()
    
    name = database.child('users').child(a).child('details').child('name').get().val()

    return render(request,'update.html',{'w':ref,'p':ref1,'d':dat,'e':name,'i':ref2})   
   
