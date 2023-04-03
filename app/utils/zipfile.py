import zipfile
from io import BytesIO


def zipFiles(files):
    zip_bytes = BytesIO()
    print(files)
    # Create a ZipFile object using the BytesIO object
    with zipfile.ZipFile(zip_bytes, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        # Add each string as a separate file to the archive
        for file in files:
            print(f"Adding {file.name} to the zip archive")
            zip_file.writestr(file.name, file.read())

    # Seek to the beginning of the BytesIO object
    zip_bytes.seek(0)
    return zip_bytes