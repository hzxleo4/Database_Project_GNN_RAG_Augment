import json
import os
def process_files(a_json_file, test_info_file, output_file):
    if not os.path.exists(output_file):
        with open(a_json_file, 'r', encoding='utf-8') as f:
            a_data = json.load(f)

        with open(test_info_file, 'r', encoding='utf-8') as f:
            test_info_lines = f.readlines()

        for a_item in a_data:
            id = a_item["id"]
            related_words = a_item["related word"]
            entity_ids = []

            for related_word in related_words:
                count = 0
                for key, values in related_word.items():
                    for value in values:
                        if value != "None" and count < 5:
                            entity_ids.append(value.replace("/", "", 1).replace("/", "."))
                            count += 1

            if not entity_ids:
                continue

            test_info_line = json.loads(test_info_lines[id - 1])
            cand = test_info_line["cand"]

            existing_entity_ids = [item[0] for item in cand]
            entity_ids.extend(existing_entity_ids)

            total_entities = len(entity_ids)
            average_value = 1.0 / total_entities

            cand = [[entity_id, average_value] for entity_id in entity_ids]

            test_info_line["cand"] = cand
            test_info_lines[id - 1] = json.dumps(test_info_line)

        with open(output_file, 'w', encoding='utf-8') as f:
            for line in test_info_lines:
                if line.strip():  
                    f.write(line.strip() + "\n")  

