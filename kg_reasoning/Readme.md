### Requirement

```Plain
python==3.9.21
torch==1.9.0+cu111
Base==0.0.0
numpy==1.21.0
torch==1.9.0+cu111
tqdm==4.67.1
transformers==4.6.1
sqlite==3.45.3
```

### Get Started

1. Download the project
2. Extract the files from the directories ./data/originalKG/cwq/ and ./data/originalKG/webqsp/, obtain ./data/originalKG/cwq/test. json and ./data/originalKG/webqsp/test. json
3. Run the program

```Plain
python main.py
```

### Workflow

1. Load the entity_id and entity_name from **./data/entity2name/entities_names.json** into the sqite3 database.

```SQL
dbCreate("./data/entity2name/entities_names.json","./data/entity2name/entities.db" )
```

1. Extract the question context  cwq and webqsp knowledge graph

```SQL
# Extract the question from CWQ knowledge graph
extractQuestionFromSrwebqsp("./data/originalKG/cwq/test.json", "./data/extractedQuestion/cwq/question.txt")

# Extract the question from Webqsp knowledge graph
extractQuestionFromSrwebqsp("./data/originalKG/webqsp/test.json", "./data/extractedQuestion/webqsp/question.txt")
```

1. Call LLM(i.e. deepseek) to abstract the related keyword based on the question

```SQL
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
```

1. Search in the sqplite3 database to find if there are any entities that contain related words

```SQL
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
 
```

1. Modify the LLM input file(e.g. /result/gnn/RoG-webqsp/rearev-lmsr/test.info) and add the retrieved entity id to the LLM input

```SQL
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
 
```