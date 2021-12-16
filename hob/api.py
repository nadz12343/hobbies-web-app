from json.decoder import JSONDecodeError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from datetime import datetime, date, timedelta
from .models import UserAccount, Hobby, FriendRequest

def GET_all_UserAccount(request):

    """
    Request: GET. Fetches UserAccount objects. Those objects are
    comapared against Hobbies the users have with the uer logged in
    and are sorted accordingly.
    """

    # Checks if method is PUT
    # This is to ensure if the request given will require filtering
    if request.method=="PUT":
        PUT = json.loads(request.body)

        age=PUT['age']
        date_format = "%Y-%d-%m"
        todays_date=datetime.strptime(date.today().strftime(date_format), date_format)

        from_date=todays_date-timedelta(days=100*365.2425)
        to_date=todays_date

        # Checks filtering option selected
        if age=='1':
            from_date=todays_date-timedelta(days=20*365.2425)
            to_date=todays_date
        elif age=='2':
            from_date=todays_date-timedelta(days=30*365.2425)
            to_date=todays_date-timedelta(days=20*365.2425)
        elif age=='3':
            from_date=todays_date-timedelta(days=50*365.2425)
            to_date=todays_date-timedelta(days=30*365.2425)
        elif age=='4':
            from_date=todays_date-timedelta(days=100*365.2425)
            to_date=todays_date-timedelta(days=50*365.2425)

        # Check if city field is empty thus not requiring a city filter
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

    similar_hobbies = {}
    
    # Gets all user with similar hobbies into a list
    for n in all_users:
        x = n.get("hobbies")
        current_hobbies=[]
        compared_user=[]
        if(len(x)>=1):
            for k in x:
                current_hobbies.append(k.get("id"))
        compared_user = list(set(list_u_hob).intersection(current_hobbies))
        if len(compared_user)>=1:
            similar_hobbies[n.get("id")] = compared_user 
    
    # Sorts the list according to the length of the list cotaining hobby IDs
    similar_hobbies = sorted(similar_hobbies.items(), key= lambda x: len(x[1]), reverse=True)

    final_users = {}

    # Creates a dictionary containing the users with similar hobbies
    for index, user in enumerate(similar_hobbies):
        u = get_object_or_404(UserAccount, id=user[0])

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
        except:
            is_friend = False

        final_users[index] = {
            'user': u.simple_dict(),
            'hobbies': hobby_dict,
            'total': len(user[1]),
            'sent_req': req_sent,
            'are_friends': is_friend,
        }

    return JsonResponse({
        'users': final_users,
    })

def GET_UserAccount(request):

    '''
    Request: GET. Fetches UserAccount objects for the currently logged in
    user. Also their friend requests are fetched.
    '''

    user = get_object_or_404(UserAccount, id=request.user.id)
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

    '''
    Request: PUT. Ne hobby is added to the Hobbies database.
    '''

    if request.method == "PUT":
        PUT = json.loads(request.body)
        u = get_object_or_404(UserAccount, id=request.user.id)
        hob = get_object_or_404(Hobby, id=PUT['id'])
        u.hobbies.add(hob)
        return JsonResponse({})

def PUT_UserAccount(request):

    '''
    Request: PUT. New User details are udpated and saved into the database.
    '''

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

def hobbies_api(request):

    '''
    Request: GET. Fetches all hobbies currently stored in the database.
    Method also adds a field to judge if the user has already added the hobby
    or not.
    '''

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

    '''
    Request: POST. Adds new row entry to the Hobby models.
    '''

    POST = json.loads(request.body)
    hobby = Hobby(
        name=POST['name'],
        description=POST['description'],
    )
    hobby.save()
    return JsonResponse({})

def send_friend_request(request, id):

    '''
    Request: POST. Adds new friend request row in FrienRequest model.
    '''

    if request.method=="POST":
        friend_request = FriendRequest(from_user=get_object_or_404(UserAccount, id=request.user.id), to_user=get_object_or_404(UserAccount, id=id))
        friend_request.save()
        return JsonResponse({})

def GET_friend_requests(request):
    
    '''
    Request: GET. Fetches all friend requests for a given user.
    '''

    return JsonResponse({
        'requests': [
            request.requests_to_dictionary()
            for request in FriendRequest.objects.filter(to_user=get_object_or_404(UserAccount, id=request.user.id))
        ]
    })

def manage_friend_request(request, id):

    '''
    Request: DELETE. Deletes row entry for friend request.
    '''

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

    '''
    Request: DELETE. Fetches all friend requests for a given user.
    '''

    if request.method=="DELETE":
        u=UserAccount.objects.get(id=request.user.id)
        hob=u.hobbies.get(id=id)
        u.hobbies.remove(hob)
        return JsonResponse({})

def get_latest_hobbies(request):

    '''
    Request: GET. Fetches all hobbies.
    '''

    return JsonResponse({
        'hobbies': [
            hobby.to_dict()
            for hobby in Hobby.objects.all()
        ]
    })