import json

def prune_structure_with_examples(data):
    """
    Recursively strips down JSON data, keeping only the FIRST element 
    of arrays to preserve structure, while keeping actual example values intact.
    """
    if isinstance(data, dict):
        # Process every key in the dictionary
        return {key: prune_structure_with_examples(value) for key, value in data.items()}
    
    elif isinstance(data, list):
        if not data:
            return []
        
        # CRITICAL STEP: Keep ONLY the first item in the list as the example structure,
        # but completely process its contents to retain its original example values.
        return [prune_structure_with_examples(data[0])]
        
    else:
        # Leave primitive values (strings, ints, bools, nulls) exactly as they are
        return data

def skeletonize_with_examples(input_file, output_file):
    print(f"Reading {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Extracting template structure with real example values...")
        structure = prune_structure_with_examples(data)
        
        print(f"Writing skeleton to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            # indent=4 gives you a pretty-printed, readable layout
            json.dump(structure, f, indent=4, ensure_ascii=False)
            
        print("Done! Example-based structure successfully saved.")
        
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Check if the file is valid.")

if __name__ == "__main__":
    # Update these paths to match your local file names
    INPUT_PATH = "mista.json"
    OUTPUT_PATH = "json_structure_with_examples.json"
    
    skeletonize_with_examples(INPUT_PATH, OUTPUT_PATH)