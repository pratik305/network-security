import os


class S3Sync:
    def sync_folder_to_s3(self, folder: str, aws_bucket_url: str):
        """Push local folder to S3 bucket"""
        command = f"aws s3 sync {folder} {aws_bucket_url}"
        os.system(command)

    def sync_folder_from_s3(self, folder: str, aws_bucket_url: str):
        """Pull from S3 bucket to local folder"""
        command = f"aws s3 sync {aws_bucket_url} {folder}"
        os.system(command)