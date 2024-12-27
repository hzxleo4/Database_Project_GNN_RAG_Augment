This project is a course project from CSCI5120.

The baseline is **GNN-RAG: Graph Neural Retrieval for Large Language Modeling Reasoning**. We modified it with LLM-based Candidate Answer Expansion and Subgraph-based Retrieval Path Expansion.


![alt GNN-RAG: The GNN reasons over a dense subgraph to retrieve candidate answers, along
with the corresponding reasoning paths (shortest paths from question entities to answers). The
retrieved reasoning paths -optionally combined with retrieval augmentation (RA)- are verbalized
and given to the LLM for RAG](pipeline.png "Pipeline")


# 1.Get started
## 1.1 Requirements
```Plain
python==3.9.21
torch==1.9.0+cu111
Base==0.0.0
numpy==1.21.0
torch==1.9.0+cu111
tqdm==4.67.1
transformers==4.6.1
sqlite3==3.45.3

pybind11==2.11.1
openai==0.27.9
trl==0.7.1
peft==0.5.0
datasets==2.14.4
accelerate==0.26.0
networkx==3.1
graph-walker==1.0.6
sentencepiece==0.2.0
```
We have requirement files in `llm/requirements.txt` , `gnn/requirements.txt` ,`kg_reasoning/requirements.txt`.

## 1.2 prepare openai api or deepseek api
By default, we provide deepseek api for quick start. For flexible deployment, you need to setup LLM api (openai/deepseek/...).

For deepseek, setup your api key as an environment variable, and update `kg_reasoning/llm.py`:
```python
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
```

## 1.3 prepare files
Please also download `entities_names.json` file from https://drive.google.com/drive/folders/1ifgVHQDnvFEunP9hmVYT07Y3rvcpIfQp?usp=sharing and put it in `llm/`, as GNNs use the dense graphs.

Please also download 'test.json' file from https://drive.google.com/drive/folders/1-wCf3DGj5xVAWkHScBrZQ3Xpy9M5WcC3?usp=sharing, and put this test.json file in `llm/results/gnn/{DATA_SET}/rearev-sbert/` and `llm/results/gnn/{DATA_SET}/rearev-lmsr/` , as LLM use the dataset as test.

Unzip the files under the directories `kg_reasoning/data/originalKG/cwq/test.zip` and `kg_reasoning/data/originalKG/webqsp/test.zip`,  to obtain two `test.json` files

## 1.4 run kg_reasoning
```shell
cd kg_reasoning
python3 main.py
```
## 1.5 move intermidiate files
We copy the results of KG reasoning to LLM module.
```
cd kg_reasoning
cp ./result/gnn/RoG-webqsp/rearev-sbert/webqsp_sbert.info ../llm/results/gnn/RoG-webqsp/rearev-sbert/test.info
cp ./result/gnn/RoG-cwq/rearev-sbert/cwq_sbert.info ../llm/results/gnn/RoG-cwq/rearev-sbert/test.info

./result/gnn/RoG-webqsp/rearev-lmsr/webqsp_lsmr.info
./result/gnn/RoG-cwq/rearev-lmsr/cwq_lmsr.info
```

## 1.6 run GNN-RAG
Note: For the first running, we need to download models (~ 15GB) from hugging face, which may take lone time.

To evaluate GNN-RAG performance, 
```shell
cd llm
time bash scripts/rag-reasoning.sh
```

We provide the final results of GNN retrieval in `results/gnn`.


# 2.repo structure
The directory is the following:

|----`gnn` folder has the implementation of different KGQA GNNs. 

You can train your own GNNs or you can skip this folder and  use directly the GNN output (retrieved answer nodes) that we computed (`llm/results/gnn`).

|----`llm` folder has the implementation for RAG-based KGQA with LLMs. 

Please see details on how to reproduce results there. 