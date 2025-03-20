import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from tqdm import tqdm
import re
from colorama import init, Fore, Style
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize colorama for colored terminal output
init(autoreset=True)

# Configure the Selenium driver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print(Fore.GREEN + "Connected to existing Chrome session.")
    return driver

# Step 1: Get all subpage links under <ul class="topics">
def get_subpage_links(driver, main_url):
    driver.get(main_url)
    
    try:
        # Wait for the topics section to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.section-item'))
        )
        topics_section = driver.find_element(By.CSS_SELECTOR, 'div.section-item')
        links = topics_section.find_elements(By.CSS_SELECTOR, 'a[href*="view.php?id="]')
        return [link.get_attribute('href') for link in links]
    except Exception as e:
        print(Fore.RED + f"Error finding subpage links: {e}")
        return []

# Step 2: Extract video URL from iframe
def get_video_url_from_iframe(driver, subpage_url):
    driver.get(subpage_url)
    
    try:
        # Wait for the iframe to be present and switch to it
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
        )
        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)
        
        # Execute JavaScript to fetch the value of the 'path' variable
        video_url = driver.execute_script("return window.Video_Url ? Video_Url : null;")
        
        if video_url:
            return video_url
        else:
            print(Fore.RED + "Failed to get video url!")
    except Exception as e:
        print(Fore.RED + f"Error extracting iframe from {subpage_url}: {e}")
        return None
        

# Step 3: Download video
def download_video(video_url, output_path):
    # Send a GET request to get the video content
    response = requests.get(video_url, stream=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Get the total file size from the Content-Length header
        total_size = int(response.headers.get('Content-Length', 0))
        
        # Initialize a progress bar with the total file size
        with open(output_path, 'wb') as file:
            # Create a tqdm progress bar
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading ") as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    # Write each chunk to the file
                    file.write(chunk)
                    # Update the progress bar
                    bar.update(len(chunk))
        
        print(Fore.GREEN + f"Downloaded: {output_path}")
    else:
        print(Fore.RED + f"Failed to download: {video_url}")

def sanitize_filename(name):
    # Define invalid characters for filenames
    invalid_chars = r'[<>:"/\\|?*]'
    # Replace invalid characters with an underscore
    sanitized_name = re.sub(invalid_chars, ' ', name)
    return sanitized_name

# First open debug instance of chrome with command:
# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium\chrome-profile"
# Then use script to download files.
# make sure `course_url` is set to the page where the subpages contain all the video iframes (e.g. Lecture Recordings page in SSS)
def main():
    driver = setup_driver()
    course_url = 'https://wuecampus.uni-wuerzburg.de/moodle/course/section.php?id=734243'
    output_dir = 'downloads'
    os.makedirs(output_dir, exist_ok=True)

    try:
        login_link = driver.find_elements(By.CSS_SELECTOR, 'a[href="https://wuecampus.uni-wuerzburg.de/moodle/login/index.php"]')
        if login_link:
            print(Fore.RED + "Login failed. Please login in chrome (the debug instance).")
            driver.quit()
            exit()
    except Exception as e:
        print(Fore.RED + f"Error checking login status: {e}")

    subpages = get_subpage_links(driver, course_url)
    print(Fore.CYAN + f"Found {len(subpages)} subpages.")

    # Start processing each subpage
    for i, subpage in enumerate(subpages, start=1):
        name = driver.title
        video_url = get_video_url_from_iframe(driver, subpage)
        
        if not video_url:
            print(Fore.YELLOW + f"Failed to get URL on page {i}/{len(subpages)} ({name}), skipping.")
            continue

        sanitized_name = sanitize_filename(name)
        filename = os.path.join(output_dir, f"{sanitized_name}.mp4")

        print(Fore.CYAN + f"\nDownloading Video {i}/{len(subpages)}: \"{name}\"")
        print(Fore.WHITE + f"URL:      \"{video_url}\"")
        print(Fore.WHITE + f"Filename: \"{filename}\"")

        if os.path.exists(filename):
            print(Fore.YELLOW + f"File already exists. Skipping download.")
        else:
            # Download the video if it does not exist
            download_video(video_url, filename)

    print(Fore.GREEN + "All subpages processed!")
    driver.quit()

if __name__ == '__main__':
    main()
