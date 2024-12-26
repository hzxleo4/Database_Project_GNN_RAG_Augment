import json
import os
def process_files(a_json_file, test_info_file, output_file):
    if not os.path.exists(output_file):
        # 读取A.json文件
        with open(a_json_file, 'r', encoding='utf-8') as f:
            a_data = json.load(f)

        # 读取test.info文件
        with open(test_info_file, 'r', encoding='utf-8') as f:
            test_info_lines = f.readlines()

        # 处理每一行
        for a_item in a_data:
            id = a_item["id"]
            related_words = a_item["related word"]
            entity_ids = []

            # 提取related word中的entity_id，每次最多添加5个entity
            for related_word in related_words:
                count = 0
                for key, values in related_word.items():
                    for value in values:
                        if value != "None" and count < 5:
                            entity_ids.append(value.replace("/", "", 1).replace("/", "."))
                            count += 1

            # 如果entity_ids为空，则跳过此行
            if not entity_ids:
                continue

            # 读取test.info中的对应行
            test_info_line = json.loads(test_info_lines[id - 1])
            cand = test_info_line["cand"]

            # 将现有的entity_id添加到entity_ids中
            existing_entity_ids = [item[0] for item in cand]
            entity_ids.extend(existing_entity_ids)

            # 计算平均值
            total_entities = len(entity_ids)
            average_value = 1.0 / total_entities

            # 更新cand
            cand = [[entity_id, average_value] for entity_id in entity_ids]

            # 更新test.info中的对应行
            test_info_line["cand"] = cand
            test_info_lines[id - 1] = json.dumps(test_info_line)

        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in test_info_lines:
                if line.strip():  # 确保行内容不为空
                    f.write(line.strip() + "\n")  # 去除多余的换行符

