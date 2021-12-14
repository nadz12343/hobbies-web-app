from json.decoder import JSONDecodeError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from datetime import datetime, date, timedelta
from .models import UserAccount, Hobby, FriendRequest

def GET_all_UserAccount(request):

    if request.method=="PUT":
        PUT = json.loads(request.body)

        age=PUT['age']
        print(age)
        date_format = "%Y-%d-%m"
        todays_date=datetime.strptime(date.today().strftime(date_format), date_format)

        from_date=todays_date-timedelta(days=100*365.2425)
        to_date=todays_date

        if age=='1':
            from_date=todays_date-timedelta(days=20*365.2425)
            to_date=todays_date
        elif age=='2':
            print("age cahnged")
            from_date=todays_date-timedelta(days=30*365.2425)
            to_date=todays_date-timedelta(days=20*365.2425)
        elif age=='3':
            from_date=todays_date-timedelta(days=50*365.2425)
            to_date=todays_date-timedelta(days=30*365.2425)
        elif age=='4':
            from_date=todays_date-timedelta(days=100*365.2425)
            to_date=todays_date-timedelta(days=50*365.2425)

        
        # print(datetime.strptime(date.today().strftime(date_format), date_format))
        # dat1=datetime.strptime(date.today().strftime(date_format), date_format)
        # dat=dat1-timedelta(days=365.2425)

        u=UserAccount.objects.exclude(id=request.user.id).filter(city=PUT['city'])
        if PUT['city']=="":
            u=UserAccount.objects.exclude(id=request.user.id)

        
        all_users = [
            users.to_dictionary_user_hobbies()
            for users in u.filter(date_of_birth__range=[from_date, to_date])
        ]
    else:
        all_users = [
        users.to_dictionary_user_hobbies()
        for users in UserAccount.objects.exclude(id=request.user.id)
        ]

    current_user = get_object_or_404(UserAccount, id=request.user.id).to_dictionary_users_hobbies()
    list_u_hob = []
    for n in current_user.get("hobbies"):
        list_u_hob.append(n.get("id"))
    print(list_u_hob)
    #print(current_user.get("hobbies")[1].get("id"))

    similar_hobbies = {}
    
    for n in all_users:
        x = n.get("hobbies")
        current_hobbies=[]
        compared_user=[]
        if(len(x)>=1):
            for k in x:
                #print(k.get("id"))
                current_hobbies.append(k.get("id"))
        compared_user = list(set(list_u_hob).intersection(current_hobbies))
        if len(compared_user)>=1:
            similar_hobbies[n.get("id")] = compared_user 
    
    similar_hobbies = sorted(similar_hobbies.items(), key= lambda x: len(x[1]), reverse=True)

    print(similar_hobbies)
    #print(all_users)

    final_users = {}

    for index, user in enumerate(similar_hobbies):
        u = get_object_or_404(UserAccount, id=user[0])
        #print(u)

        hobby_dict = {}
        for index1, hobby in enumerate(user[1]):
            hobby_dict[index1] = get_object_or_404(Hobby, id=hobby).to_dict()

        req_sent = True
        is_friend = True

        try:
            FriendRequest.objects.get(from_user=get_object_or_404(UserAccount, id=request.user.id), to_user=u)
        except:
            req_sent = False

        try:
            UserAccount.objects.get(id=request.user.id).friends.get(id=u.id)
            print("they are friends")
        except:
            is_friend = False
            print("they are not friends")
        
        print("Request sent: "+str(req_sent))

        

        final_users[index] = {
            'user': u.simple_dict(),
            'hobbies': hobby_dict,
            'total': len(user[1]),
            'sent_req': req_sent,
            'are_friends': is_friend,
        }

    print(final_users)

    return JsonResponse({
        'users': final_users,
    })

def GET_UserAccount(request):
    #GET_all_UserAccount(request)
    user = get_object_or_404(UserAccount, id=request.user.id)
    #request = FriendRequest.objects.filter(to_user=get_object_or_404(UserAccount, id=request.user.id))
    return JsonResponse({
        'user': [
            user.to_dictionary_full_info(),
        ],
        'requests': [
            friend_request.requests_to_dictionary()
            for friend_request in FriendRequest.objects.filter(to_user=get_object_or_404(UserAccount, id=request.user.id))
        ],
    })

def add_hobby_user_list(request):
    if request.method == "PUT":
        PUT = json.loads(request.body)
        u = get_object_or_404(UserAccount, id=request.user.id)
        hob = get_object_or_404(Hobby, id=PUT['id'])
        u.hobbies.add(hob)
        return JsonResponse({})

def PUT_UserAccount(request):
    if request.method == "PUT":
        user = get_object_or_404(UserAccount, id=request.user.id) 
        PUT = json.loads(request.body)
        user.first_name=PUT['firstname']
        user.last_name=PUT['lastname']
        user.username=PUT['username']
        user.city=PUT['city']
        user.email=PUT['email']
        user.date_of_birth=PUT['dob']
        user.save()
        return JsonResponse({})

def get_uesr_age(user):
    date_format = "%Y-%d-%m"
    today = date.today()
    a = datetime.strptime(str(user.date_of_birth), date_format)
    b = datetime.strptime(today.strftime(date_format), date_format)
    print(a)
    delta = b - a
    print(delta.days/365.2425)
    return delta.days/365.2425

def hobbies_api(request):

    allHobbies = [
        hobby.to_dict()
        for hobby in Hobby.objects.all()
    ]

    allHobbiesv2 = {}
    for i,x in enumerate(allHobbies):
        allHobbiesv2[i] = {
            'hob': x,
            'is_added': UserAccount.objects.get(id=request.user.id).hobbies.filter(id=x.get('id')).exists()
        }

    return JsonResponse({
        'hobbies': allHobbiesv2,
    })

def addHobby_api(request):
    POST = json.loads(request.body)
    hobby = Hobby(
        name=POST['name'],
        description=POST['description'],
    )
    hobby.save()
    return JsonResponse({})

def send_friend_request(request, id):
    if request.method=="POST":
        friend_request = FriendRequest(from_user=get_object_or_404(UserAccount, id=request.user.id), to_user=get_object_or_404(UserAccount, id=id))
        friend_request.save()
        return JsonResponse({})

def GET_friend_requests(request):
    #request = FriendRequest.objects.filter(to_user=get_object_or_404(UserAccount, id=request.user.id))
    return JsonResponse({
        'requests': [
            request.requests_to_dictionary()
            for request in FriendRequest.objects.filter(to_user=get_object_or_404(UserAccount, id=request.user.id))
        ]
    })

def manage_friend_request(request, id):
    if request.method=="DELETE":
        DELETE=json.loads(request.body)
        action=DELETE['action']
        receiver=get_object_or_404(UserAccount, id=request.user.id)
        sender=get_object_or_404(UserAccount, id=id)
        friend_request = FriendRequest.objects.get(from_user=sender, to_user=receiver)

        if action=="accept":
            receiver.friends.add(sender)
            sender.friends.add(receiver)
        
        friend_request.delete()
        return JsonResponse({})

def remove_hobby_from_list(request, id):
    if request.method=="DELETE":
        u=UserAccount.objects.get(id=request.user.id)
        hob=u.hobbies.get(id=id)
        u.hobbies.remove(hob)
        return JsonResponse({})

def get_latest_hobbies(request):
    return JsonResponse({
        'hobbies': [
            hobby.to_dict()
            for hobby in Hobby.objects.all()
        ]
    })