import boto3


class S3DriveManager(object):

    def base_path(self):
        raise ImplementationError('To be implemented')

    def _check_folder_exists(self, data, prefix):
        if data.get('CommonPrefixes', None):
            return True
        elif data.get('Contents', None):
            for content in data['Contents']:
                if content['Size'] == 0 and content['Key'] == prefix:
                    return True
        return False

    def create_folder(self, name, path):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3 = session.resource('s3')
        base_path = self.base_path()
        if name:
            # Folder path to contain only a-z A-Z 0-9 _ - / characters in it
            if path and not bool(re.match('^[a-zA-Z0-9_\-/]+$', path)):
                raise Exception("Folder path can contain only alphabets, numbers, '_' and '-' in it", content_type="text/plain")
            # Folder name to contain only a-z A-Z 0-9 _ - characters in it
            if not bool(re.match('^[a-zA-Z0-9_\-]+$', name)):
                raise Exception("Folder name can contain only alphabets, numbers, '_' and '-' in it", content_type="text/plain")
            data = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).meta.client.list_objects(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Prefix=base_path + path,
                Delimiter='/'
            )
            if path and not _check_folder_exists(data, base_path + path):
                raise Exception("Folder path does not exist", content_type="text/plain")
            prefix = base_path + path + name + '/'
            data = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).meta.client.list_objects(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Prefix=prefix,
                Delimiter='/'
            )
            if _check_folder_exists(data, prefix):
                raise Exception("Folder already exists", content_type="text/plain")
            data = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=prefix)
            return "Created folder successfully"
        raise Exception("Folder name cannot be empty")

    def get_files(self, name, path):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3 = session.resource('s3')
        base_path = self.base_path()

        # To get all the files and folders in a directory
        # if folder_name is empty it will fetch the files and folders
        # from root folder
        # TODO: Exclude all the files with size 0
        prefix = base_path + path
        data = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).meta.client.list_objects(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix=prefix,
            Delimiter='/'
        )

        folders = data.get('CommonPrefixes', [])
        files = data.get('Contents', [])
        file_paths = [file['Key'] for file in files]

        return {
            "is_present": len(folders) or len(files),
            "files": file_paths,
            "folders": folders
        }

    def get_folders(self, page, path):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3 = session.resource('s3')
        base_path = self.base()

        # To get all the files and folders in a directory
        # if folder_name is empty it will fetch the files and folders
        # from root folder
        # TODO: Exclude all the files with size 0
        prefix = base_path + path
        data = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).meta.client.list_objects(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix=prefix,
            Delimiter='/'
        )

        breadcrumbs = []
        for key, val in enumerate(path.split('/')):
            breadcrumbs.append('/'.join(path.split('/')[:key]))

        breadcrumbs = breadcrumbs[1:]

        folders = data.get('CommonPrefixes', [])
        files = data.get('Contents', [])
        file_paths = [file['Key'] for file in files]

        return {
            "is_present": len(folders) or len(files),
            "files": file_paths,
            "folders": folders
        }

    def create_folder(self, name, path):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3 = session.resource('s3')
        base_path = self.base_path()
        if name:
            # Folder path to contain only a-z A-Z 0-9 _ - / characters in it
            if path and not bool(re.match('^[a-zA-Z0-9_\-/]+$', path)):
                raise Exception("Folder path can contain only alphabets, numbers, '_' and '-' in it", content_type="text/plain")
            # Folder name to contain only a-z A-Z 0-9 _ - characters in it
            if not bool(re.match('^[a-zA-Z0-9_\-]+$', name)):
                raise Exception("Folder name can contain only alphabets, numbers, '_' and '-' in it", content_type="text/plain")
            data = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).meta.client.list_objects(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Prefix=base_path + path,
                Delimiter='/'
            )
            if path and not _check_folder_exists(data, base_path + path):
                raise Exception("Folder path does not exist", content_type="text/plain")
            prefix = base_path + path + name + '/'
            data = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).meta.client.list_objects(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Prefix=prefix,
                Delimiter='/'
            )
            if _check_folder_exists(data, prefix):
                raise Exception("Folder already exists", content_type="text/plain")
            data = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=prefix)
            return "Created folder successfully"
        raise Exception("Folder name cannot be empty")

    def delete_folder():
        raise ImplementationError('Not implemeneted!')

    def rename_folder():
        raise ImplementationError('Not implemeneted!')
