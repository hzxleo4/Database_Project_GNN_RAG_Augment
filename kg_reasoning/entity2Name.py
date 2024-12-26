import sqlite3
import os
import re

def create_database(file_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS entities (entity_id TEXT PRIMARY KEY, entity_name TEXT)")
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t', 1)
            if len(parts) == 2:
                entity, name = parts
                cursor.execute("INSERT OR IGNORE INTO entities (entity_id, entity_name) VALUES (?, ?)", (entity, name))
            else:
                print(f"Skipping line: {line.strip()}")
    conn.commit()
    conn.close()

def search_entity_name(db_path, entity_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT entity_name FROM entities WHERE entity_id = ?", (entity_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Entity ID not found"

def convert_entity_id(entity_id):
    match = re.match(r"([a-zA-Z])\.(.+)", entity_id)
    if match:
        return f"/{match.group(1)}/{match.group(2)}"
    return entity_id


# def main():
#     file_path = 'mid2name.txt'
#     db_path = 'entities.db'
#     entity_id = '/m/0kmn7'
#     if not os.path.exists(db_path):
#         create_database(file_path, db_path)
#     result = search_entity_name(db_path, entity_id)
#     print(result)

def read_entities(file_path):
    with open(file_path, 'r') as file:
        entities = file.read().splitlines()
    converted_entities = [convert_entity_id(entity) for entity in entities]
    return converted_entities

def save_entity_to_file(entity, entity_name, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"{entity}: {entity_name}\n")

def transfer():
    entity_file = 'entities.txt'
    output_file = 'entity_names.txt'

    entity2name_file = 'mid2name.txt'
    db_path = 'entities.db'

    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        create_database(entity2name_file, db_path)
    
    entities = read_entities(entity_file)
    for entity_id in entities:
        result = search_entity_name(db_path, entity_id)
        save_entity_to_file(entity_id, result, output_file)

    print(f"Entity names saved to {output_file}")


if __name__ == '__main__':
    transfer()









