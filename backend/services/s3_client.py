"""
S3 client for video storage operations.
"""
import boto3
import os
from typing import Optional
from uuid import UUID
from botocore.exceptions import ClientError
import mimetypes


class S3Client:
    """
    S3 client for uploading and managing video assets.
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize S3 client.

        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key
            region: AWS region
        """
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET", "video-foundry-dev")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

        # Initialize boto3 client
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region
        )

    def upload_file(
        self,
        file_path: str,
        s3_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload a file to S3.

        Args:
            file_path: Local path to the file
            s3_key: S3 object key (path in bucket)
            content_type: MIME type (auto-detected if not provided)

        Returns:
            S3 URL of the uploaded file

        Raises:
            ClientError: If upload fails
        """
        if content_type is None:
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or "application/octet-stream"

        extra_args = {"ContentType": content_type}

        self.s3_client.upload_file(
            file_path,
            self.bucket_name,
            s3_key,
            ExtraArgs=extra_args
        )

        return self.get_url(s3_key)

    def upload_fileobj(
        self,
        file_obj,
        s3_key: str,
        content_type: str = "video/mp4"
    ) -> str:
        """
        Upload a file object to S3.

        Args:
            file_obj: File-like object
            s3_key: S3 object key
            content_type: MIME type

        Returns:
            S3 URL of the uploaded file
        """
        extra_args = {"ContentType": content_type}

        self.s3_client.upload_fileobj(
            file_obj,
            self.bucket_name,
            s3_key,
            ExtraArgs=extra_args
        )

        return self.get_url(s3_key)

    def download_file(self, s3_key: str, local_path: str):
        """
        Download a file from S3.

        Args:
            s3_key: S3 object key
            local_path: Local path to save the file

        Raises:
            ClientError: If download fails
        """
        self.s3_client.download_file(
            self.bucket_name,
            s3_key,
            local_path
        )

    def delete_file(self, s3_key: str):
        """
        Delete a file from S3.

        Args:
            s3_key: S3 object key

        Raises:
            ClientError: If deletion fails
        """
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=s3_key
        )

    def get_url(self, s3_key: str) -> str:
        """
        Get the public URL for an S3 object.

        Args:
            s3_key: S3 object key

        Returns:
            Public URL for the object
        """
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

    def get_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate a presigned URL for temporary access.

        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds

        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {e}")

    def generate_segment_key(self, project_id: UUID, segment_id: UUID) -> str:
        """
        Generate S3 key for a segment video.

        Args:
            project_id: Project UUID
            segment_id: Segment UUID

        Returns:
            S3 key path
        """
        return f"segments/{project_id}/{segment_id}.mp4"

    def generate_final_video_key(self, project_id: UUID, render_job_id: UUID) -> str:
        """
        Generate S3 key for a final rendered video.

        Args:
            project_id: Project UUID
            render_job_id: Render job UUID

        Returns:
            S3 key path
        """
        return f"renders/{project_id}/{render_job_id}.mp4"
