import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig

class Embedder:
    def __init__(self, pretty_name, model_name="Alibaba-NLP/gte-multilingual-base", max_length=8192):
        self.model_name=model_name
        self.pretty_name = pretty_name
        self.max_length=max_length

        # Check if CUDA is available before configuring BitsAndBytes
        if torch.cuda.is_available():
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                quantize_in_4bit=True,
            )
            device = torch.device("cuda")
        else:
            quantization_config = None
            device = torch.device("cpu")

        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True, quantization_config=quantization_config).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, max_length=max_length, trust_remote_code=True, truncation=True)

        if device.type == 'cuda':
            self.model = torch.compile(self.model)

        self.model.eval()
        self.device = self.model.device

    def process_batch(self, examples):
        vecs = self.dense_encode(examples['text'])
        if len(vecs.shape) == 1:
            vecs = vecs.reshape(1, -1)
        vecs = vecs.tolist()

        return {
            'embeddings': vecs,
            'doc': examples['doc'],
            'page': examples['page'],
            'text': examples['text'],
            'title': examples['title']
        }

    def dense_encode(self, text):
        if isinstance(text, str):
            text = [text]

        batch_dict = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=self.max_length, padding='longest').to(self.device)

        with torch.no_grad():
            outputs = self.model(**batch_dict)

        dimension=768
        embeddings = outputs.last_hidden_state[:, 0, :]
        if embeddings.shape[-1] != dimension:
             print(f"Warning: Model output dimension ({embeddings.shape[-1]}) does not match expected dimension ({dimension}). Using available dimension.")
             dimension = embeddings.shape[-1]
             embeddings = outputs.last_hidden_state[:, 0, :]

        embeddings = F.normalize(embeddings, p=2, dim=1).squeeze().cpu().detach().numpy()
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        return embeddings[0] if len(embeddings) == 1 else embeddings


embedding = Embedder(pretty_name="GTE Multilingual Base")
