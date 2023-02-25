
import boto3
from config import OBJECT_STORAGE_CONFIG
import subprocess
from pathlib import Path

client = boto3.client("s3", **OBJECT_STORAGE_CONFIG)


def saveS3File(localFilename, bucketFilename):
    client.upload_file(
        Filename=localFilename,
        Bucket='assets.repables.com',
        Key=bucketFilename,
        ExtraArgs={'ACL':'public-read'})

def scan_file(filename):
    scanCommand = subprocess.run(['clamdscan', filename], capture_output=True)
    result = scanCommand.stdout
    resultArr = result.decode().split("\n")
    checkArr = resultArr[0].split(" ")
    if checkArr[-1] == "OK":
        return False
    else:
        Path(filename).unlink()
        return True