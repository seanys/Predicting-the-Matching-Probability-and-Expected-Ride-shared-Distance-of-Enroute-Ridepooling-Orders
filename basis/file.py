import requests
import progressbar
import zipfile
import os
import shutil


def downloadFileFromGoogleDrive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = getConfirmToken(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    if destination == "datasets.zip" or destination == "matching_relationship.zip":
        saveResponseContent(response, destination, CHUNK_SIZE = 12000) 
        return

    saveResponseContent(response, destination, CHUNK_SIZE = 32768) 

def getConfirmToken(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def saveResponseContent(response, destination, CHUNK_SIZE):
    with open(destination, "wb") as f:
        bar = progressbar.ProgressBar(max_value=CHUNK_SIZE,widgets=["Datasets Downloading:", progressbar.Percentage(),' (', progressbar.SimpleProgress(), ') ',' (', progressbar.AbsoluteETA(), ') ',])
        i = 0
        for chunk in bar(response.iter_content(CHUNK_SIZE)):
            if chunk:
                f.write(chunk)
            i = 1 + i
            bar.update(i)
            # print(i)

def decompression(name):
    zFile = zipfile.ZipFile("%s.zip"%name, "r")
    for fileM in zFile.namelist(): 
        zFile.extract(fileM, "")
    zFile.close()

    if os.path.exists("%s.zip"%name):
        os.remove("%s.zip"%name)

    if os.path.exists("__MACOSX"):
        shutil.rmtree("__MACOSX")

    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__")

def downloadDatasets():
    '''Download datasets for simulation'''
    file_id = '1yi3aNhB6xc1vjsWX5pq9eb5rSyDiyeRw' # Chunk Size 2634(3000)
    destination = 'datasets.zip'
    downloadFileFromGoogleDrive(file_id, destination)
    decompression("datasets")

def downloadMatchingRelationship():
    '''Download data for prediction'''
    file_id = '1RNEmGBfnm-nIP32m3R1oj4pK8Oxmm7EO' # Chunk Size 2634(3000)
    destination = 'matching_relationship.zip'
    downloadFileFromGoogleDrive(file_id, destination)
    decompression("matching_relationship")


if __name__ == "__main__":
    # file_id = '10i5V5jTZd8sO3ryFtXYRmbHNrYcEF5FZ' # 测试的小文件
    # file_id = '1yi3aNhB6xc1vjsWX5pq9eb5rSyDiyeRw' # 数据集合，Chunk Size 2634，设置为3000
    # destination = 'datasets.zip'
    downloadDatasets()
    # downloadFileFromGoogleDrive(file_id, destination)
    # decompression("datasets.zip")

