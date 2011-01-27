from django.core.files.uploadedfile import TemporaryUploadedFile

def move_rawdata_to_files(func):
    def decorate(request, *args, **kwargs):
        if request.method == 'POST' and 'HTTP_X_FILE_NAME' in request.META:
            tf = TemporaryUploadedFile('rawdata', request.META['HTTP_X_FILE_TYPE'], int(request.META['CONTENT_LENGTH']), None)
            chunk = ' '
            while len(chunk) > 0:
                chunk = request.read(1024)
                tf.write(chunk)
            tf.seek(0)
            request.FILES['file'] = tf
        return func(request, *args, **kwargs)
    return decorate
