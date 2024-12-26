from openai import OpenAI
import os
import json

# 设置OpenAI API密钥
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def parse_entity_name(line):
    return eval(line.strip())

def generate_related_work(question):

    client = OpenAI(api_key="sk-a6e7f33f34504b0d9b6123916e6736cf", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": f"Question: {question}. Abstract this question and generate 5 high-level abstracted related keyword(1 to 3 words) which can give the key observation of this question. The related keyword should not exixts in the question. There is not any underscores in the keywordPlease just give me the keyword, do not return any sectence and any number to point the order. Please return the answer in this format: keyword1,keyword2,keyword3,keyword4,keyword5.  "}
        ],
        stream=False
    )
    return response.choices[0].message.content

def filter_and_clean_lines(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # 删除每行中的*符号
            cleaned_line = line.replace('*', '')
            # 检查行是否以1. 2. 3. 4. 5.开头
            if cleaned_line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                outfile.write(cleaned_line)
    os.remove(input_file)
    os.rename(output_file, input_file)


def process_related_word(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        records = []
        record_id = 1
        current_record = {}

        for line in infile:
            line = line.strip()
            if line:
                if not current_record:
                    current_record["id"] = record_id
                    current_record["question"] = line
                else:
                    related_words = [{word.strip(): "None"} for word in line.split(',') if word.strip()]
                    current_record["related word"] = related_words
                    records.append(current_record)
                    current_record = {}
                    record_id += 1

        json.dump(records, outfile, ensure_ascii=False, indent=4)


def generate_related_word(question_file, output_file, output_json_file): 
    if not os.path.exists(output_file):
        questions = read_file(question_file) 
        with open(output_file, 'w', encoding='utf-8') as outfile: 
            for question in questions: 
                print("question=", question) 
                related_word = generate_related_work(question.strip()) 
                print("related_word=", related_word) 
                outfile.write(f"{question}{related_word}\n\n")

        process_related_word(output_file, output_json_file)


input_file ="./data/relatedWord/webqsp/relatedWord.txt"
output_file = "./data/relatedWord/webqsp/relatedWord.json"
process_related_word(input_file, output_file)


