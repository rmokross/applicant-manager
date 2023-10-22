from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import time

app = Flask(__name__)
CORS(app)

timer_start_timer = None
TIMER_DURATION = 6000 # 100 Min

@app.route('/timer/start', methods=['POST'])

def start_timer():
    global timer_start_time
    timer_start_time = time.time()
    return jsonify({"message": "Timer started!"}), 200

@app.route('/timer/status', methods=['GET'])

def get_timer_status():
    if timer_start_time is None:
        return jsonify({"error": "Timer hasn't started yet!"}), 400


    elapsed_time = time.time() - timer_start_time
    remaining_time = TIMER_DURATION - elapsed_time

    if remaining_time <= 0:
        status = "Timer finished!"
        remaining_time = 0

    else:
        status = "Timer is running."


    return jsonify({
        "status": status,
        "elapsed_time": elapsed_time,

        "remaining_time": remaining_time

    }), 200

@app.route('/applicants', methods=['POST'])
def add_applicant():
    # Extract applicant data from the request
    data = request.json
    user_name = data.get('user_name')

    # Create an IAM client
    client = boto3.client('iam')

    try:

        # Create User 
        response = client.create_user(UserName=user_name, Path="/Bewerber/")
        # Create a login profile for the user
        response = client.create_login_profile(
            UserName=user_name,
            Password="Fisch123",
            PasswordResetRequired=False
        )
        response = client.add_user_to_group(
            GroupName="Bewerber-Accounts",
            UserName=user_name
        )
        return jsonify({"message": "Applicant added successfully!", "response_1": response}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route('/applicants', methods=['GET'])
def get_applicants():
    # Create an IAM client
    client = boto3.client('iam')
    
    try:
        applicants = client.list_users(
            
        )
        return (applicants), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/positions', methods=['GET'])
def get_positions():
    positions = [{
        "tile": "TEST",
        "date": "2023-10-10"
    }]
    return jsonify({"positions": positions}), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = [{
        "tile": "TEST",
        "date": "2023-10-10"
    }]
    return jsonify({"tasks": tasks}), 200

@app.route('/c9_start', methods=['POST'])
def start_c9_env():
    data = request.json
    create_c9_data = data.get('createC9')
    add_c9_member = data.get('envMember')
    # Create C9 client
    client = boto3.client('cloud9')
    r = {"createC9": {},
         "envMember": {}}
    try:
        response = client.create_environment_ec2(**create_c9_data)
        r["createC9"] = response
        add_c9_member["environmentId"] = response["environmentId"]
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # Create C9 member
    time.sleep(60)
    try:
        response = client.create_environment_membership(**add_c9_member)
        r["envMember"] = response
        return jsonify(r), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400
    
@app.route('/c9_stop', methods=['POST'])
def stop_c9_env():
    data = request.json
    env_id = data.get('environmentId')
    client = boto3.client('c9')
    try:
        response = client.delete_environment(
            environmentId=env_id
        )
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/set_egress', methods = ["POST"])
def enable_egress():
    client = boto3.client('ec2')
    try:
        response = client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':

                    # This allows only one ec2 instance to run at a time
                    instance_id = instance['InstanceId']  
                    security_group = instance['SecurityGroups'][0]['GroupId']
                    instance_name = instance['Tags'][1]['Value']
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    ip_permissions = [
            {
                'FromPort': 443,
                'ToPort': 443,
                'IpProtocol': 'tcp',
                'PrefixListIds': [
                    {
                        'PrefixListId': "pl-63a5400a" # security group prefix
                    }
                ]
            }
        ]    

    try:
        response = client.authorize_security_group_egress(
            GroupId=security_group,
            DryRun=False,
            IpPermissions=ip_permissions
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    revoke_ip_permissions = [
        {
            'FromPort'      :   -1,
            'IpProtocol'    :   'all',
            'ToPort'        :   -1,
            'IpRanges': [
                {
                    'CidrIp':   '0.0.0.0/0'
                }
            ]
        }
    ]
    try:
        response = client.revoke_security_group_egress(
                GroupId=security_group,
                IpPermissions=revoke_ip_permissions
                )
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/set_ingress_open', methods = ['POST'])
def set_ingress():
    data = request.json
    ip_address = data.get('IpAddress')

    client = boto3.client('ec2')
    try:
        response = client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':

                    # This allows only one ec2 instance to run at a time
                    instance_id = instance['InstanceId']  
                    security_group = instance['SecurityGroups'][0]['GroupId']
                    instance_name = instance['Tags'][1]['Value']
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    ip_permissions = [
            {
                'FromPort': 22,
                'ToPort': 22,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': ip_address
                    }
                ]
            }
        ]    

    try:
        response = client.authorize_security_group_ingress(
            GroupId=security_group,
            DryRun=False,
            IpPermissions=ip_permissions
            )
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400    
    
@app.route('/get_instace_ip', methods = ['GET'])
def get_instance_ip():
    client = boto3.client('ec2')
    try:
        response = client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':

                    # This allows only one ec2 instance to run at a time
                    instance_ip = instance['PublicIpAddress']
        return jsonify({"Ip": instance_ip}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400    

if __name__ == '__main__':
    app.run(debug=True)

