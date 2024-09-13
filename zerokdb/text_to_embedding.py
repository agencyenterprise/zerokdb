from transformers import AutoTokenizer, AutoModel


class TextToEmbedding:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def convert(self, text):
        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True
        )
        outputs = self.model(**inputs)
        # Mean pooling to get the sentence embedding
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.detach().numpy().tolist()[0]
