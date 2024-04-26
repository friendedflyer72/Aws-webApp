import boto3
import json
# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id="ASIAXYKJVXP7XE6JOQ3M",
                          aws_secret_access_key="bpw5XMnw9f0fl69Ilx4aRBLuq8nG5Q8uhjMSHV78",
                          aws_session_token=r"IQoJb3JpZ2luX2VjEDAaCXVzLXdlc3QtMiJGMEQCICbjW2YxB/3i6IuXu4i4zjPncX+XyGSYSGDo2iUCMaoeAiB0zFYHggCTQ6Xe24y8om7g2KqXIcF2iPQSuHm/SLFD7yq2AghpEAAaDDUzMzI2NzMzMjA5NSIM2oMYEnpi3agoZO3mKpMCE0PJF+ShXotkv+WLcq7F+qRTB/iVh0mO1rWMx+hcN+nvW68Lx4zZ3aF1FBj3nxPhA632h+wI2l/ukZdU+BU/I+X0akbRNtim/xV5VX3QGsM9vk/ersqXF+wQLR9l1f150Mzk4/9KBiu9QCHnm72mtZwmLYGMfJHRq3U9seOdmOJewm6pEANEnelhkO1a0ymv1dQLiYdWUx5pKCrvB2ZxsyEBR9KKCV27lGDPwrX0LrmqfhMuVAUT55g3/VbmgXzXoXCFUnXyBFhKEyGH0I++9cJJKipNC+YlHed/5RdLy068kSdYr+0YYoKSASZcGi7LSxAIZycfoLMC0hOFKSXBg0Q+1O8/A5rc27TBLjhHWl8h+LIws53nsAY6ngHPr7oq3ZauWS2pUunDmblMf79bQA+9hVPLKUaR+FzjqOf4yYuTiowcjk1db1EFpNoHd+9F2qZ9/LZOUERl7jDkkh8C0vdIt9Jvf1NO4hwykx1N/LEb2E0WTLmkxbS0Hemxfz5zTw0Nwfx8GpJachYzTYnNlHFVMqGp5Ue0719FaSzG44lVx2sKzUEijCK3MC8IplRQNey0x69Ac+xAYA==",
                          region_name="us-east-1")

# Task 1.1
def create_login_table():
    try:
        table = dynamodb.create_table(
            TableName='login',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'  # PartitionedKey
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        print("Table Status:", table.table_status)
    except Exception as e:
        print("Error Creating login Table:", e)


# Function to insert data into the login table
def insert_login_data():
    try:
        table = dynamodb.Table('login')
        for i in range(10):
            email = f"s3960290{i}@student.rmit.edu"
            user_name = f"Samiran Das{i}"
            password = f"{i}12345"
            item = {
                'email': email,
                'user_name': user_name,
                'password': password
            }
            table.put_item(Item=item)
    except Exception as e:
        print("Error Inserting Items", e)

# Task 1.2: Create a "music" table in DynamoDB
def create_music_table():
    try:
        table = dynamodb.create_table(
            TableName='music',
            KeySchema=[
                {
                    'AttributeName': 'title',
                    'KeyType': 'HASH'  # Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'title',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        print("Table Status:", table.table_status)
        # Wait for the table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName='music')
    except Exception as e:
        print("Error creating Music table ", e)

 # Task 1.3: Load data from a JSON file into the "music" table
def load_data_from_json(json_file):
    try:
        table = dynamodb.Table('music')
        with open(json_file) as f:
            data = json.load(f)
            songs = data.get('songs', [])  # Extracting the list of songs
            for song in songs:
                table.put_item(Item=song)   
    except Exception as e:
        print("Error Uploading Data", e)

# Call the functions to execute the tasks
# create_login_table()
# insert_login_data()
create_music_table()
load_data_from_json('a1.json')