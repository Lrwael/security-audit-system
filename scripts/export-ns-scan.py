import requests
import urllib3
import time

# Suppress TLS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NESSUS_API = "https://192.168.59.184:32002"
ACCESS_KEY = "bbc8c1f4e31c5392035fbad134fdc9416b823d3f2708d16c0a1d4b2dfc86522c"  # Replace with your access key
SECRET_KEY = "bbfc3915d4817e8275ef0e13f6e55312b34c18f2cf95d5b786cad393665b6831"  # Replace with your secret key

headers = {"X-ApiKeys": f"accessKey={ACCESS_KEY}; secretKey={SECRET_KEY}"}

# Initiate the export request
scan_id = 5  # Replace with your scan ID
export_url = f"{NESSUS_API}/scans/{scan_id}/export"
export_payload = {"format": "csv"}  # Use csv format for easier parsing

# Step 1: Request the export
response = requests.post(export_url, headers=headers, json=export_payload, verify=False)
if response.status_code == 200:
    file_id = response.json().get("file")
    print(f"Export initiated. File ID: {file_id}")
else:
    print(f"Error initiating export: {response.status_code}, {response.text}")
    exit()

# Step 2: Poll export status
status_url = f"{NESSUS_API}/scans/{scan_id}/export/{file_id}/status"
while True:
    status_response = requests.get(status_url, headers=headers, verify=False)
    if status_response.status_code == 200:
        status = status_response.json().get("status")
        print(f"Export status: {status}")
        if status == "ready":
            break
        elif status == "error":
            print("Error during export.")
            exit()
    else:
        print(f"Error checking status: {status_response.status_code}, {status_response.text}")
        exit()
    time.sleep(5)  # Wait before polling again

# Step 3: Download the exported file
download_url = f"{NESSUS_API}/scans/{scan_id}/export/{file_id}/download"
download_response = requests.get(download_url, headers=headers, verify=False)

if download_response.status_code == 200:
    with open(f"./scans/scan_{scan_id}.csv", "wb") as file:
        file.write(download_response.content)
    print(f"Scan report downloaded: ./scan_{scan_id}.csv")
else:
    print(f"Error downloading file: {download_response.status_code}, {download_response.text}")


