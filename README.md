# How to use
First open debug instance of chrome with command:
```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium\chrome-profile"
```
Then use script to download files.
Set `course_url` in the script to the page where the subpages contain all the video iframes (e.g. Lecture Recordings page in SSS)

then you can run the script with
```
python moodle-video-downloader.py
```

# Dependencies

Tested with Python 3.11

Install dependencies with
```
pip install selenium webdriver-manager requests tqdm colorama
```
