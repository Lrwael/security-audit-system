import csv
import requests
import re
import json
# Server URL
OLLAMA_SERVER_URL = "http://192.168.47.42:8889/api/generate"

def clean_prompt(prompt):
    cleaned_prompt = re.sub(r'[^\x20-\x7E]', '', prompt)  # Remove non-ASCII characters
    return cleaned_prompt

# Function to read a CSV file and generate a prompt
def generate_prompt_from_csv(csv_file):

    prompt = f"The file {csv_file} contains the results of a Nessus vulnerability scan.\n\n"
    prompt += "Below are the first 5 rows of the data for your review:\n\n"

    with open(csv_file, 'r', encoding='utf-8-sig') as file:  # Try 'utf-8-sig' for autodetection
        reader = csv.reader(file)
        headers = next(reader)
        prompt += ", ".join(headers) + "\n"
        for i, row in enumerate(reader):
            if i >= 5:  # Only read the first 5 rows
                break
            prompt += ", ".join(row) + "\n"

    prompt += (
        "\nUsing the data provided:\n"
        "1. Identify and analyze the critical, high, and medium severity vulnerabilities.\n"
        "2. Explain the potential risks associated with these vulnerabilities.\n"
        "3. Provide detailed, actionable recommendations to mitigate each vulnerability.\n"
        "4. Highlight any potential patterns or trends in the scan data that could indicate broader issues.\n"
        "Ensure your analysis is clear and concise, using professional language tailored for a cybersecurity report.\n"
    )
    return prompt

# Function to query Ollama server
def query_ollama(prompt, model="llama3.1"):
    try:
        # Prepare the payload
        payload = {
            "model": model,
            "prompt": prompt
        }
        # Stream the POST request to the server
        response = requests.post(OLLAMA_SERVER_URL, json=payload, stream=True)

        # Check for errors in the response
        response.raise_for_status()

        # Aggregate the "response" fields from the JSON objects
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)  # Parse each line as JSON
                    full_response += data.get("response", "")  # Append the "response" field
                except json.JSONDecodeError:
                    print(f"Error decoding line: {line}")  # Log problematic lines
                    continue

        return full_response.strip()
    except requests.RequestException as e:
        return f"Error querying the Ollama server: {e}"

# Main function
def main():
    csv_file = "./scans/scan_5.csv"  # Replace with the path to your CSV file
    output_file = "analysis_scan.txt"

    # Generate the prompt from the CSV file
    prompt = clean_prompt(generate_prompt_from_csv(csv_file))
    print(f"Generated Prompt:\n{prompt}")

    # Obtain the model's response
    response = query_ollama(prompt)
    print(f"Model Response:\n{response}")

    # Save the response to a text file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(response)
    print(f"Analysis saved in: {output_file}")

if __name__ == "__main__":
    main()
