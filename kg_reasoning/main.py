import json
import sqlite3
import os
import re
from llm import generate_related_word
from entity2Name import transfer
from inputProcess import process_files

# 阶段1
def dbCreate(input_file, db_path):
    if not os.path.exists(db_path):
        print("Trigger dbCreate")
        # 读取JSON文件
        with open(input_file, 'r') as f:
            data = json.load(f)

        # 连接到SQLite数据库（如果数据库不存在，则会自动创建）
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建表（如果表不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_name TEXT
            )
        ''')

        # 插入数据
        for entity_id, entity_name in data.items():
            cursor.execute('''
                INSERT OR REPLACE INTO entities (entity_id, entity_name)
                VALUES (?, ?)
            ''', (entity_id, entity_name))

        # 提交事务并关闭连接
        conn.commit()
        conn.close()


# 阶段2
def extract_question_entities_to_dict(json_file):
    question_entities_dict = {}
    with open(json_file, 'r', encoding='utf-8') as infile:
        for line_number, line in enumerate(infile, start=1):
            data = json.loads(line.strip())
            if 'entities' in data:
                question_entities_dict[line_number] = data['entities']
    return question_entities_dict

def extract_question_to_dict(json_file):
    question_dict = {}
    with open(json_file, 'r', encoding='utf-8') as infile:
        for line_number, line in enumerate(infile, start=1):
            data = json.loads(line.strip())
            if 'question' in data:
                question_dict[line_number] = data['question']
    return question_dict

def save_dict_to_file(dictionary, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for key, value in dictionary.items():
            file.write(f"{value}\n")

def extractQuestionFromSrwebqsp(json_file, target_question):
    if not os.path.exists(target_question):
        question_dict = extract_question_to_dict(json_file)
        save_dict_to_file(question_dict,target_question )

        print(f"question dictionary saved to {target_question}")


# 阶段3：调用LLM，根据已有question抽象出related keyword

# 阶段4：在sqlite数据库中进行搜索，判断是否有entity包含了keyword
def process_related_word(input_file, db_file, output_file):
    if not os.path.exists(output_file):
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as infile:
            records = json.load(infile)

        # 处理每条记录
        for record in records:
            related_words = record["related word"]
            for word_dict in related_words:
                for keyword in word_dict.keys():
                    # 在数据库中查找包含keyword的entity
                    cursor.execute("SELECT entity_id FROM entities WHERE entity_name LIKE ?", ('%' + keyword + '%',))
                    results = cursor.fetchall()
                    if results:
                        word_dict[keyword] = [result[0] for result in results]
                    else:
                        word_dict[keyword] = ["None"]

        # 将更新后的记录写入输出文件
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(records, outfile, ensure_ascii=False, indent=4)

        # 关闭数据库连接
        conn.close()




if __name__ == '__main__':
    # 阶段1：创建sqlite数据库，将已有entity2name加载到数据库中
    dbCreate("./data/entity2name/entities_names.json","./data/entity2name/entities.db" )

    # 阶段2：提取cwq与webqsp数据集json文件中的question信息
    extractQuestionFromSrwebqsp("./data/originalKG/cwq/test.json", "./data/extractedQuestion/cwq/question.txt")
    extractQuestionFromSrwebqsp("./data/originalKG/webqsp/test.json", "./data/extractedQuestion/webqsp/question.txt")

    # # 阶段3：调用LLM，根据已有的question抽象出related keyword
    generate_related_word(
        "./data/extractedQuestion/cwq/question.txt",
        "./data/relatedWord/cwq/relatedWord.txt",
        "./data/relatedWord/cwq/relatedWord.json"
        )

    generate_related_word(
        "./data/extractedQuestion/webqsp/question.txt",
        "./data/relatedWord/webqsp/relatedWord.txt",
        "./data/relatedWord/webqsp/relatedWord.json"
        )
    
    # # 阶段4：在sqplite3数据库中进行搜索，判断是否有entity包含了相关的related word
    process_related_word(
        "./data/relatedWord/cwq/relatedWord.json",
        "./data/entity2name/entities.db",
        "./data/relatedWord/cwq/cwq_final_relatedWord.json"
        )

    process_related_word(
        "./data/relatedWord/webqsp/relatedWord.json",
        "./data/entity2name/entities.db",
        "./data/relatedWord/webqsp/webqsp_final_relatedWord.json"
        )
    
    # 阶段5:修改llm输入文件，将检索到的entity_id加入到llm输入的candiate中
    process_files(
        "./result/gnn/RoG-webqsp/webqsp_final_relatedWord.json",
        "./result/gnn/RoG-webqsp/rearev-lmsr/test.info",
        "./result/gnn/RoG-webqsp/rearev-lmsr/update_test.info"
    )

    process_files(
        "./result/gnn/RoG-webqsp/webqsp_final_relatedWord.json",
        "./result/gnn/RoG-webqsp/rearev-sbert/test.info",
        "./result/gnn/RoG-webqsp/rearev-sbert/update_test.info"
    )

    process_files(
        "./result/gnn/RoG-cwq/cwq_final_relatedWord.json",
        "./result/gnn/RoG-cwq/rearev-lmsr/test.info",
        "./result/gnn/RoG-cwq/rearev-lmsr/update_test.info"
    )

    process_files(
        "./result/gnn/RoG-cwq/cwq_final_relatedWord.json",
        "./result/gnn/RoG-cwq/rearev-sbert/test.info",
        "./result/gnn/RoG-cwq/rearev-sbert/update_test.info"
    )