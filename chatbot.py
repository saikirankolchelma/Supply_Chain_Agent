import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import LLMResult, Generation
from huggingface_hub import InferenceClient
from database import SupplyChainDB


class CustomLLM(BaseLLM):
    client: InferenceClient

    def __init__(self, client: InferenceClient):
        super().__init__(client=client)

    def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
        responses = []
        for prompt in prompts:
            response = self.client.text_generation(prompt, max_new_tokens=100)
            responses.append(response)
        generations = [[Generation(text=r)] for r in responses]
        return LLMResult(generations=generations)

    def _call(self, prompt: str, stop=None, **kwargs) -> str:
        return self.client.text_generation(prompt, max_new_tokens=100)

    @property
    def _llm_type(self) -> str:
        return "custom_hf_inference"


class SupplyChainChatbot:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Validate API key
        api_key = os.getenv("HF_API_KEY")
        if not api_key:
            raise ValueError("API key is required but not provided. Please set the HF_API_KEY environment variable.")

        # Initialize InferenceClient
        self.client = InferenceClient(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            token=api_key
        )

        # Initialize other components
        self.template = """
        You are a supply chain assistant. Provide a concise, clear response to the user's query based on the data provided.
        Query: {query}
        Data: {data}
        Response:
        """
        self.llm = CustomLLM(self.client)
        self.prompt = PromptTemplate(input_variables=["query", "data"], template=self.template)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.db = SupplyChainDB()

    def handle_query(self, query: str) -> str:
        query_lower = query.lower()
        if "stock" in query_lower:
            product = self._extract_product(query)
            if not product:
                return "Please provide a valid product name."
            data = self.db.check_stock(product)
            if "No data available" in data:
                return f"Sorry, I couldn't find any information about {product}."
        elif "order" in query_lower:
            order_id = self._extract_order_id(query)
            if not order_id.isdigit():
                return "Please provide a valid order ID."
            data = self.db.check_order_status(order_id)
        elif "price" in query_lower:
            product = self._extract_product(query)
            if not product:
                return "Please provide a valid product name."
            data = self.db.check_price(product)
        else:
            product = self._extract_product(query)
            if not product:
                return "Please provide a valid product name."
            stock = self.db.check_stock(product)
            price = self.db.check_price(product)
            order_result = self.db.conn.execute("SELECT order_id, order_status FROM supply_chain WHERE LOWER(product_name) = ?", (product.lower(),)).fetchone()
            if order_result:
                order_id, order_status = order_result
                data = f"{stock} {price} Order #{order_id} is {order_status}."
            else:
                data = f"{stock} {price} No order data available."
        response = self.chain.run(query=query, data=data)
        return response.strip()

    def _extract_product(self, query: str) -> str:
        words = query.split()
        if "of" in query:
            product = words[words.index("of") + 1]
        else:
            product = words[-1].strip("?").strip(".")  # Remove trailing punctuation
        print(f"Extracted product: {product}")  # Debug log
        return product.lower()  # Normalize to lowercase

    def _extract_order_id(self, query: str) -> str:
        return "".join([w for w in query.split() if w.isdigit()]) or "123"