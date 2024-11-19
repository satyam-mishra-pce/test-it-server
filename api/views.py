from os import path, remove
import subprocess
from uuid import uuid4
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.exceptions import CompilationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Contest, Problem, User,TestCase, Submission
from config.settings import BASE_DIR
from django.db.models import Q
from rest_framework import serializers
import time
from rest_framework import parsers

@api_view(['post'])
@permission_classes([])
def get_token(request):
    data = request.data
    user = authenticate(username=data['username'],password=data['password'])
    if user:
        refresh = RefreshToken.for_user(user)

        return Response({
            'id':user.id,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'username':user.username,
            'email':user.email,
            'phone':user.phone,
            'batch':user.batch,
            'branch':user.get_branch_display(),
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

@api_view(['post'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])
def compile(request):
    data = request.data
    lang = data.get('lang')
    code = data.get('code')
    pid = data.get('pid')
    # problem = Problem.objects.get(id=pid) 
    testcases = TestCase.objects.filter(problem=pid) # TODO Cache this result
    _filename = f'test_{uuid4()}.{lang}'
    _fileloc = path.join(BASE_DIR,"media","cache",_filename)
    with open(_fileloc, 'w') as fp:
        fp.write(r'{}'.format(code))
        fp.close()
    try :
        if lang == "py": 
            outputs = []
            for testcase in testcases:
                _output  = subprocess.run(
                    ["python3",_fileloc],
                    input=testcase.input_data.encode('utf-8'),
                    timeout=3,
                    capture_output=True
                    )
                if _output.stdout.decode('utf-8') == testcase.expected_output:
                    outputs.append(_output)
                else:
                    break
            remove(_fileloc)
        elif lang == "js": 
            
            outputs = []
            for testcase in testcases:
                _output  = subprocess.run(
                    ["node",_fileloc],
                    input=testcase.input_data.encode('utf-8'),
                    timeout=3,
                    capture_output=True
                    )
                if _output.stdout.decode('utf-8') == testcase.expected_output:
                    outputs.append(_output)
                else:
                    break
            # remove(_fileloc)
        elif lang == "cpp": 
            _output  = subprocess.run(
                ["g++",_fileloc],
                timeout=5,
                capture_output=True
                )
            # remove(_fileloc)
            if _output.returncode != 0:
                ctx = _output.stderr.decode('utf-8')
                return Response(ctx,status=status.HTTP_400_BAD_REQUEST)
            outputs = []
            for testcase in testcases:
                _output = subprocess.run(
                    [f'./a.out'],
                    input=testcase.input_data.encode('utf-8'),
                    timeout=1,
                    capture_output=True
                    )
                if _output.stdout.decode('utf-8') == testcase.expected_output:
                        outputs.append(_output)
                else:
                    break
            remove('./a.out')
        elif lang == "c": 
            _output  = subprocess.run(
                ["gcc",_fileloc],
                timeout=5,
                capture_output=True
                )
            remove(_fileloc)
            if _output.returncode != 0:
                ctx = _output.stderr.decode('utf-8')
                return Response(ctx,status=status.HTTP_400_BAD_REQUEST)
            outputs = []
            for testcase in testcases:
                _output = subprocess.run(
                    [f'./a.out'],
                    input=testcase.input_data.encode('utf-8'),
                    timeout=1,
                    capture_output=True
                    )
                if _output.stdout.decode('utf-8') == testcase.expected_output:
                        outputs.append(_output)
                else:
                    break
            remove('./a.out')
        else:
            return Response('Language not supported.',status=status.HTTP_403_FORBIDDEN)
    except CompilationError as e:
        print("Error : ",e.__str__())
    except RuntimeError as e:
        print("Error : ",e.__str__())
    except Exception as e:
        print("Error : ",e.__str__())
        return Response(f'Error : {e.__str__()}',status=status.HTTP_400_BAD_REQUEST)
    ctx = _output.stdout.decode('utf-8')
    if _output.returncode != 0:
        ctx = _output.stderr.decode('utf-8')
        return Response(ctx,status=status.HTTP_400_BAD_REQUEST)
    return Response(ctx)
    

@api_view(['GET'])
def get_problems(request):
    """
    Get a problem (DSA questions)
    """
    try:
        problem = Problem.objects.get(id=request.GET.get("id"))
        json = {
                'id': problem.id,
                'title': problem.title,
                'description': problem.description,
                'input': problem.input,
                'output': problem.output,
                'constraints': problem.constraints,
                'difficulty': problem.difficulty,
                'points': problem.points
            }
        return Response(json, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(f'Error: {str(e)}', status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET']) 
def get_contests(request):
    """
    Get all contests with their associated problems
    """
    try:
        contests = Contest.objects.prefetch_related('problems').filter(Q(branch="ALL") | Q(branch=request.user.branch))
        contests_list = []
        for contest in contests:
            problems = []
            for problem in contest.problems.all():
                problems.append({
                    'id': problem.id,
                    'title': problem.title,
                    'points': problem.points,
                    'difficulty': problem.difficulty
                })
            contests_list.append({
                'id': contest.id,
                'name': contest.name,
                'description': contest.description,
                'start_time': contest.start_time,
                'end_time': contest.end_time,
                'problems': problems
            })
        return Response(contests_list, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(f'Error: {str(e)}', status=status.HTTP_400_BAD_REQUEST)


class RunTestCasesSerializer(serializers.Serializer):
    lang = serializers.CharField()
    code = serializers.CharField()


@api_view(['POST'])
def submission(request):
    serializer = RunTestCasesSerializer(data=request.data)
    if serializer.is_valid():
        lang = serializer.validated_data['lang']
        code = serializer.validated_data['code']
        problem_id = request.data.get('pid')  # Ensure 'pid' is included in the request
        
        # Fetch test cases from the database based on the problem ID
        testcases = TestCase.objects.filter(problem_id=problem_id).values('input_data', 'expected_output', 'visible')
        
        _filename = f'test_{uuid4()}.{lang}'
        _fileloc = path.join(BASE_DIR, "media", "cache", _filename)
        
        with open(_fileloc, 'w') as fp:
            fp.write(code)
        
        outputs = []
        passed_count = 0
        failed_cases = []
        start_time = time.time()
        
        try:
            for testcase in testcases:
                input_data = testcase['input_data']
                expected_output = testcase['expected_output']
                is_visible = testcase['visible']
                
                if lang == "py":
                    _output = subprocess.run(
                        ["python3", _fileloc],
                        input=input_data.encode('utf-8'),
                        timeout=3,
                        capture_output=True
                    )
                elif lang == "js":
                    _output = subprocess.run(
                        ["node", _fileloc],
                        input=input_data.encode('utf-8'),
                        timeout=3,
                        capture_output=True
                    )
                elif lang == "cpp":
                    _output = subprocess.run(
                        [f'./a.out'],
                        input=input_data.encode('utf-8'),
                        timeout=1,
                        capture_output=True
                    )
                elif lang == "c":
                    _output = subprocess.run(
                        [f'./a.out'],
                        input=input_data.encode('utf-8'),
                        timeout=1,
                        capture_output=True
                    )
                else:
                    return Response('Language not supported.', status=status.HTTP_403_FORBIDDEN)

                output = _output.stdout.decode('utf-8').rstrip()
                if output== expected_output.rstrip():

                    outputs.append({"input": input_data, "output": output, "status": "Passed"})
                    passed_count += 1
                else:
                    if is_visible:
                        outputs.append({"input": input_data, "output": output, "status": "Failed", "expected": expected_output})
                        failed_cases.append({"input": input_data, "expected": expected_output, "actual": output})
                    else:
                        outputs.append({"input": input_data, "status": "Failed (hidden)"})

        finally:
            remove(_fileloc)  

        time_taken = time.time() - start_time 

        submission = Submission.objects.create(
            user=request.user,  
            problem_id=problem_id,
            status='A' if passed_count == len(testcases) else 'R',  
            detail=str(outputs),
            passed_testcases=passed_count,
            total_testcases=len(testcases)
        )

        return Response({
            "problem_id": problem_id,
            "testcases_passed": passed_count,
            "failed_cases": failed_cases,
            "time_taken": time_taken,
            "language": lang,
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def run_code(request):
    """
    Run code based on the provided language and input.
    """
    data = request.data
    lang = data.get('lang')
    code = data.get('code')
    input_data = data.get('input')  # Get input from the request

    _filename = f'test_{uuid4()}.{lang}'
    _fileloc = path.join(BASE_DIR, "media", "cache", _filename)

    with open(_fileloc, 'w') as fp:
        fp.write(code)

    try:
        if lang == "py":
            _output = subprocess.run(
                ["python3", _fileloc],
                input=input_data.encode('utf-8'),
                timeout=3,
                capture_output=True
            )
        elif lang == "js":
            _output = subprocess.run(
                ["node", _fileloc],
                input=input_data.encode('utf-8'),
                timeout=3,
                capture_output=True
            )
        elif lang == "cpp":
            _output = subprocess.run(
                ["g++", _fileloc],
                timeout=5,
                capture_output=True
            )
            if _output.returncode != 0:
                ctx = _output.stderr.decode('utf-8')
                return Response(ctx, status=status.HTTP_400_BAD_REQUEST)
            _output = subprocess.run(
                ["./a.out"],
                input=input_data.encode('utf-8'),
                timeout=1,
                capture_output=True
            )
        elif lang == "c":
            _output = subprocess.run(
                ["gcc", _fileloc],
                timeout=5,
                capture_output=True
            )
            if _output.returncode != 0:
                ctx = _output.stderr.decode('utf-8')
                return Response(ctx, status=status.HTTP_400_BAD_REQUEST)
            _output = subprocess.run(
                ["./a.out"],
                input=input_data.encode('utf-8'),
                timeout=1,
                capture_output=True
            )
        else:
            return Response('Language not supported.', status=status.HTTP_403_FORBIDDEN)

        output = _output.stdout.decode('utf-8')
        if _output.returncode != 0:
            output = _output.stderr.decode('utf-8')
            return Response(output, status=status.HTTP_400_BAD_REQUEST)

        return Response({"output": output}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(f'Error: {str(e)}', status=status.HTTP_400_BAD_REQUEST)
