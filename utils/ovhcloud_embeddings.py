import requests

class OVHCloudEmbeddings:
    def __init__(self, model_name, access_token, endpoint_url=None):
        self.model_name = model_name
        self.access_token = access_token
        self.endpoint_url = endpoint_url or "https://api.ovh.com/ai/api-inference/v1/embeddings"

    def embed_documents(self, texts):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "inputs": texts
        }
        response = requests.post(self.endpoint_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["embeddings"]

    def embed_query(self, text):
        return self.embed_documents([text])[0]