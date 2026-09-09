import os
import urllib.request
 
DATA_DIR = "data"
 
FILES = {
    "KDDTrain+.txt": "https://raw.githubusercontent.com/jmnwong/NSL-KDD-Dataset/master/KDDTrain%2B.txt",
    "KDDTest+.txt": "https://raw.githubusercontent.com/jmnwong/NSL-KDD-Dataset/master/KDDTest%2B.txt",
}
 
 
def download():
    os.makedirs(DATA_DIR, exist_ok=True)
    for filename, url in FILES.items():
        dest = os.path.join(DATA_DIR, filename)
        if os.path.exists(dest):
            print(f"[skip] {filename} already exists")
            continue
        print(f"[downloading] {filename} ...")
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"[done] saved to {dest}")
        except Exception as e:
            print(f"[FAILED] could not download {filename}: {e}")
            print("Download it manually and place it in the data/ folder — see the docstring at the top of this file.")
 
 
if __name__ == "__main__":
    download()
 