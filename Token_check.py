# -*- coding: utf-8 -*-
import tiktoken


class TokenCounter:
    def __init__(self, model="gpt-4-0613"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            self.encoding = tiktoken.get_encoding("cl100k_base")
        self.tokens_per_message = None
        self.tokens_per_name = None
        self.set_token_counts()

    def set_token_counts(self):
        if self.model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            self.tokens_per_message = 3
            self.tokens_per_name = 1
        elif self.model == "gpt-3.5-turbo-0301":
            self.tokens_per_message = 4
            self.tokens_per_name = -1
        elif "gpt-3.5-turbo" in self.model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            self.model = "gpt-3.5-turbo-0613"
            self.set_token_counts()
        elif "gpt-4" in self.model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            self.model = "gpt-4-0613"
            self.set_token_counts()
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {self.model}.""")

    def num_tokens_from_messages(self, messages):
        """Return the number of tokens used by a list of messages."""
        num_tokens = 0
        for message in messages:
            num_tokens += self.tokens_per_message
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))
                if key == "name":
                    num_tokens += self.tokens_per_name
        num_tokens += 3  # every reply is primed with assistant
        return num_tokens


if __name__ == "__main__":
    # Create an instance of TokenCounter
    counter = TokenCounter()
    # Test the method
    # messages = [{"role": "user", "content": "你好吗？"},{"role": "user", "content": "你好吗？？"}]
    with open(r"C:\Users\Tongzou\Desktop\新建文本文档.txt", "r", encoding="utf-8") as file:
        messages1 = file.read()

    messages = [{"role": "user", "content": "你好吗？"},{"role": "user", "content": "{}".format(messages1)}]
    token_count = counter.num_tokens_from_messages(messages)
    print(token_count)
