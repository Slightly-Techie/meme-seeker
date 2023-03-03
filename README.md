# meme-seeker

## Description
The project features include;

    * Save media (image/gif/video) from twitter to Database and S3 bucket
    * Tweet the media upon request

## Sample config.ini

[twitter]

    consumer_key=xxx
    consumer_secret=xxxx
    access_token_default=xxxx
    access_secret_default=xxxxx
    access_token=xxx
    access_secret=xxx
    username=xxxxx

[database]

    name=xxxx
    user=xxxxx
    password=xxxxx

[aws_credentials]

    aws_access_key=xxxxxxxxxxxx
    aws_secret_access_key=xxxxxxxxxxxxxxxxxxxx
    aws_storage_bucket=xxxxxxxxxxxxxxx
    aws_default_acl = None

## Known Issues
* AWS S3 transfer module has an issue directly creating the object on S3 using streaming to transfer bytes objects. (https://github.com/boto/boto3/issues/3221). Due to this, I have to create the video file locally before copying to S3, then delete it. I have downgraded the python version to 3.8 to enable me upload files to s3

