import boto3
import json
import os
import requests


# s3 = boto3.resource('s3')
# Initialize DynamoDB client
s3 = boto3.client('s3',
                          aws_access_key_id="ASIAXYKJVXP73IAEQ3MY",
                          aws_secret_access_key="vb4gTfRMdXDF0ecnRLrWWVA3VAkRK9FAKHqdPrWu",
                          aws_session_token=r"IQoJb3JpZ2luX2VjEHkaCXVzLXdlc3QtMiJHMEUCICTHkSdA0rX84v5KSdjQSViMG16Njo6hFQy5VpHhN5imAiEA41ud8Pa1Gz6ozGQkdHqMJy5NsZA101OgMm5mnF1SizcqvwIIsv//////////ARAAGgw1MzMyNjczMzIwOTUiDE/2UooCmKqJEJXxbSqTAi49l925hW4qzLflGTu+oDew4Wiko4lx4h0IKxhh0jl1Epz1srpVO+S2bI1OIO7LNDw6HjjJXkLq2MfcIUksSMdsfTMtjW2AEff1oVHGmVhZ800f3kPyHONcXyq4uXU2PAyLM3AF003q2H0m7kjaKV3Smyyov/hQ4EelG7G1si9/cfCh19bPiVUaqPN8PHNNpfAP/4xPC7cqXPXxm9M89k4nxWeR370bzbnNjJb0/lNyajqsQDayZS8h4Fmyo+aMFH5fhZCiNi6Uwq6LIzIXt9HJ5h9cLKY9SN3SjBkQVXyJA0h+NpJ6mcNW6+9N8eM9L2QvnWDN/EQeTXoMcDMDMd4x0/y/ICLsUdVGKpCfpI8oT2xjMNOi97AGOp0BGLgv1vkianDXEXFjyYt6FBNoyyn8nQiOVxafq0kpz8ZMsykvuI7C8y4aWrUZ7E4Q+RYIeN7AVc7gDJBNTBu8tUOi6dS9wjMsjDyVMJnqyCsUaSm8EsCDO5p+Lq/yvgpZvAVmN8XcckyAM4xIPR9eYdJ0SlJ0SmWuuWAOxD52+utbzqTqABxopxH1xLXDvPepioaMdX392SAwnFU8/g==",
                          region_name="us-east-1")

# Function to create a new S3 bucket
def create_s3_bucket(bucket_name):
    try:
        s3.create_bucket(Bucket=bucket_name)
    except Exception as e:   
        print("Error creating bucket", e)

# Function to download images to a temporary folder
def download_images(json_file):
    temp_dir = 'temp_images'
    os.makedirs(temp_dir, exist_ok=True)

    with open(json_file) as f:
        data = json.load(f)
        songs = data.get('songs', [])

        for song in songs:
            image_url = song.get('img_url')
            if image_url:
                image_filename = image_url.split('/')[-1]
                local_image_path = os.path.join(temp_dir, image_filename)
                response = requests.get(image_url)
                with open(local_image_path, 'wb') as img_file:
                    img_file.write(response.content)

    return temp_dir
 
# Function to upload images to S3 bucket
def upload_images_to_s3(temp_dir, bucket_name):
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            local_image_path = os.path.join(root, file)
            s3.upload_file(local_image_path, bucket_name, file)
            print(f"Uploaded {file} to S3 bucket: {bucket_name}")

# Cleanup temporary folder
# def cleanup_temp_folder(temp_dir):
#     for root, dirs, files in os.walk(temp_dir, topdown=False):
#         for file in files:
#             os.remove(os.path.join(root, file))
#         for dir in dirs:
#             os.rmdir(os.path.join(root, dir))
#     os.rmdir(temp_dir)

bucket_name = 's3960290'
create_s3_bucket(bucket_name)
images = download_images('a1.json')
upload_images_to_s3(images, bucket_name)