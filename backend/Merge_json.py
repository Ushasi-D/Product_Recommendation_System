import json
import os

# List your processed files specifically
files_to_merge = [
    'all_processed.json', 
    'appliances_processed.json', 
    'beauty_processed.json', 
    'cellphones_processed.json', 
    'electronics_processed.json', 
    'fashion_processed.json'
]

output_file = 'final_master_dataset.jsonl'

with open(output_file, 'w', encoding='utf-8') as outfile:
    for file_name in files_to_merge:
        if os.path.exists(file_name):
            with open(file_name, 'r') as infile:
                data = json.load(infile)
                # Assuming each file is a list of product dictionaries
                for product in data:
                    # Ensure every product has a 'category' key before saving
                    # if 'category' not in product: product['category'] = file_name.split('_')[0]
                    outfile.write(json.dumps(product) + '\n')
            print(f"Merged {file_name}")

print(f"✅ Master file created: {output_file}")