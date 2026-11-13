import json
import csv
import pathlib

INPUT_FILE = "prahaBR.json"
OUTPUT_FILE = "prahaBR.csv"

# If you want to convert the cleaned file instead, change INPUT_FILE to:
# INPUT_FILE = "/mnt/data/jobs_praha_cleaned.json"

def json_to_csv(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("JSON file is empty")
        return

    # If JSON is a dict containing a list, try to find the list
    if isinstance(data, dict):
        # find first list value
        for v in data.values():
            if isinstance(v, list):
                data = v
                break

    if not isinstance(data, list):
        raise ValueError("Expected JSON to be a list of objects")

    # Collect all unique keys to use as CSV header (preserve order from first item)
    fieldnames = []
    for item in data:
        for k in item.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    print(f"Converting {len(data)} records")
    print(f"Columns: {fieldnames}")

    with open(output_path, "w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in data:
            # Ensure all values are strings and handle newlines in 'raw' field
            cleaned_row = {k: (str(v).replace('\r', ' ').replace('\n', ' | ') if v is not None else "") for k, v in row.items()}
            writer.writerow(cleaned_row)

    print(f"Saved CSV to: {output_path}")

if __name__ == "__main__":
    json_to_csv(INPUT_FILE, OUTPUT_FILE)
