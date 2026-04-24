import zipfile, os

def parse_zip(path):
    files = []

    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall("temp/extracted")

    for root, _, filenames in os.walk("temp/extracted"):
        for f in filenames:
            files.append(os.path.join(root, f))

    return files