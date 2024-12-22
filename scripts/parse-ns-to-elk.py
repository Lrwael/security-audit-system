import csv
from elasticsearch import Elasticsearch

# Initialize Elasticsearch client with authentication
es = Elasticsearch(
    ["https://192.168.59.184:30547"],
    basic_auth=("elastic", "nS28MLALgOph3xQg"),  # Replace with your credentials
    verify_certs=False
)

# Read the Nessus CSV report and index each row as a document
csv_file = "./scans/scan_5.csv"

with open(csv_file, mode="r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Push each row as a document into Elasticsearch
        es.index(index="nessus-reports", document=row)

print(f"Successfully indexed the findings from {csv_file} to Elasticsearch.")

