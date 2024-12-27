import time
import os
from openai import OpenAI
from .base_language_model import BaseLanguageModel
import dotenv
import tiktoken

dotenv.load_dotenv()

# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_KEY = "sk-a6e7f33f34504b0d9b6123916e6736cf"


class DeepSeek(BaseLanguageModel):
    
    @staticmethod
    def add_args(parser):
        parser.add_argument('--retry', type=int, help="retry time", default=5)
        parser.add_argument('--max_tokens', type=int, help="Max tokens for the model", default=8192)
    
    def __init__(self, args):
        super().__init__(args)
        self.retry = args.retry
        self.maximun_token = args.max_tokens  # 设置最大token限制
        self.redundant_tokens = 150  # 冗余 token 数，稍微减少实际使用的token数量
    def tokenize(self, text):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
            num_tokens = len(encoding.encode(text))
        except KeyError:
            raise KeyError(f"Warning: model {self.model_name} not found.")
        return num_tokens + self.redundant_tokens
    
    def prepare_for_inference(self, model_kwargs={}):
        '''
        ChatGPT model does not need to prepare for inference
        '''
        pass
    def generate_sentence(self, llm_input):
        query = [{"role": "user", "content": llm_input}]
        cur_retry = 0
        num_retry = self.retry
        # Chekc if the input is too long
        input_length = self.tokenize(llm_input)
        if input_length > self.maximun_token:
            print(f"Input lengt {input_length} is too long. The maximum token is {self.maximun_token}.\n Right tuncate the input to {self.maximun_token} tokens.")
            llm_input = llm_input[:self.maximun_token]
        while cur_retry <= num_retry:
            try:
                client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
                # response = openai.ChatCompletion.create(
                #     model=self.model_name,
                #     messages= query,
                #     request_timeout = 30,
                #     )
                response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=query,
                        request_timeout = 30,
                    )
                result = response["choices"][0]["message"]["content"].strip() # type: ignore
                return result
            except Exception as e:
                print("Message: ", llm_input)
                print("Number of token: ", self.tokenize(llm_input))
                print(e)
                time.sleep(30)
                cur_retry += 1
                continue
        return None