import json
import os

input_file = 'final_master_dataset.jsonl'
output_file = 'categories.txt'

categories = set()

if os.path.exists(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    product = json.loads(line)
                    category = product.get('category', 'Unknown')
                    categories.add(str(category))
                except json.JSONDecodeError:
                    pass

with open(output_file, 'w', encoding='utf-8') as f:
    for cat in sorted(categories):
        f.write(cat + '\n')
print("Categories extracted to categories.txt")
