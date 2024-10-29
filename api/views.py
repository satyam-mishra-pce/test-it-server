from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.permissions import AllowOptionsAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import User

@api_view(['post'])
@permission_classes([])
def get_token(request):
    data = request.data
    user = authenticate(email=data['email'],password=data['password'])
    if user:
        refresh = RefreshToken.for_user(user)

        return Response({
            'id':user.id,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    else:
        return Response({"error":"Incorrect email/password"},status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['post'])
@permission_classes([])
def register_user(request):
    """Registers new users through API 
    .....
    Args:
        name:str
        email:str
        password:str
        confirm-password:str
    Todo:
        Implement email verification
    """
    
    data = request.data
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    password0 = data.get("confirm-password")
    name = name.split()
    if password == password0:
        try :
            user = User.objects.create_user(
                first_name=name[0], 
                last_name=name[-1],
                email=email, 
                password=password
                )
            refresh = RefreshToken.for_user(user)
            return Response({
                'id':user.id,
                'first_name':user.first_name,
                'last_name':user.last_name,
                'email':user.email,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        except Exception as e:
            print(e)
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({"error":"User already Exists"},status=status.HTTP_401_UNAUTHORIZED)
            user.is_active = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'id':user.id,
                'first_name':user.first_name,
                'last_name':user.last_name,
                'email':user.email,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
    else:
        return Response({"error":"Password mismatch"},status=status.HTTP_401_UNAUTHORIZED)

    
"""Synchronous code compilation without IO piping, will be useful in running 
test-case based programs"""    

# @api_view(['post'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])
# def run(request):
#     user = request.user
#     lang = request.POST.get('lang')
#     code = request.POST.get('code')
#     stdin = request.POST.get('stdin')
#     _filename = f'test_{uuid4()}.{lang}'
#     _fileloc = path.join(BASE_DIR,"media",_filename)
#     with open(_fileloc, 'w') as fp:
#         # fp.write(code)
#         fp.write(r'{}'.format(code))
#         fp.close()
#     try :
#         if lang == "py": 
#             _output  = subprocess.run(["python3",_fileloc],input=stdin.encode('utf-8'),timeout=5,capture_output=True)
#             _output  = subprocess.Popen(["python3",_fileloc],input=stdin.encode('utf-8'),timeout=5,capture_output=True)
#             _output.pid
#             _output = subprocess.Popen()
#             remove(_fileloc)
#         elif lang == "js": 
#             _output  = subprocess.run(["node",_fileloc],input=stdin.encode('utf-8'),timeout=5,capture_output=True)
#             remove(_fileloc)
#         elif lang == "cpp": 
#             _output  = subprocess.run(["g++",_fileloc],timeout=5,capture_output=True)
#             remove(_fileloc)
#             if _output.returncode != 0:
#                 ctx = _output.stderr.decode('utf-8')
#                 return Response(ctx,status=status.HTTP_400_BAD_REQUEST)
#             _output = subprocess.run([f'./a.out'],input=stdin.encode('utf-8'),timeout=5,capture_output=True)
#             remove('./a.out')
#         elif lang == "c": 
#             _output  = subprocess.run(["gcc",_fileloc],timeout=5,capture_output=True)
#             remove(_fileloc)
#             if _output.returncode != 0:
#                 ctx = _output.stderr.decode('utf-8')
#                 return Response(ctx,status=status.HTTP_400_BAD_REQUEST)
#             _output = subprocess.run([f'./a.out'],input=stdin.encode('utf-8'),timeout=5,capture_output=True)
#             remove('./a.out')
#         elif lang == "dart": 
#             _output  = subprocess.run(["dart",_fileloc],input=stdin.encode('utf-8'),timeout=5,capture_output=True)
#             remove(_fileloc)
#         else:
#             return Response('Language not supported.',status=status.HTTP_403_FORBIDDEN)
#     except Exception as e:
#         print("Error : ",e.__str__())
#         return Response(f'Error : {e.__str__()}',status=status.HTTP_400_BAD_REQUEST)
#     ctx = _output.stdout.decode('utf-8')
#     if _output.returncode != 0:
#         ctx = _output.stderr.decode('utf-8')
#         return Response(ctx,status=status.HTTP_400_BAD_REQUEST)
#     return Response(ctx)
    

