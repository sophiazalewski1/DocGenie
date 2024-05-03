import gradio as gr
# from pinecone_text.sparse import BM25Encoder
from langchain_community.document_loaders import TextLoader
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS  # Not directly used, but referenced for context
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from pinecone import Pinecone, ServerlessSpec
from mistralai.client import MistralClient#, ChatMessage
# from langchain_community.retrievers import PineconeHybridSearchRetriever
from langchain_mistralai import MistralAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_pinecone import PineconeVectorStore  
# from langchain_community.embeddings import HuggingFaceEmbeddings # has dimension 384

# from langchain_community.document_loaders import Str
################################################################################
############################## BACK END (Rag) ##################################
################################################################################

class PineconeManager:
    def __init__(
            self, 
            pinecone_api_key,
            mistral_api_key, 
            environment='us-west1-gcp', 
            index_name="invalid",
            score_threshold=0.9,
            top_k_documents=2
            ):
        """
        Initialize the Pinecone manager with the API key and environment.
        """
        self.pinecone_api_key = pinecone_api_key
        self.mistral_api_key = mistral_api_key
        self.environment = environment
        self.pinecone = Pinecone(api_key=self.pinecone_api_key)
        index_spec = {
                "serverless": {
                    "cloud": "aws",
                    "region": "us-west-2"
                    }  
                }
        if index_name not in self.pinecone.list_indexes().names():
            self.pinecone.create_index(name=index_name,dimension=1024,metric='cosine', spec=index_spec)

        self.mistral_client = MistralClient(api_key = self.mistral_api_key)
        
       
        # building the retriever
        self.embeddings = MistralAIEmbeddings(model="mistral-embed", mistral_api_key=self.mistral_api_key)
        # HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.index = self.pinecone.Index(name=index_name)
        vectorstore = PineconeVectorStore(self.index, self.embeddings)  
        self.retriever = vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": score_threshold,"k": top_k_documents}) 

        # https://github.com/pinecone-io/examples/blob/master/learn/search/hybrid-search/ecommerce-search/ecommerce-search.ipynb
        # https://docs.pinecone.io/guides/data/encode-sparse-vectors
        # pinecone.init(api_key=self.api_key, environment=self.environment)

    def add_data(self, documentPath):
        """
        Create a new index in Pinecone.
        """
        loader = TextLoader(documentPath)
        docs = loader.load()
        # split by semantics: https://python.langchain.com/docs/modules/data_connection/document_transformers/semantic-chunker/
        text_splitter = RecursiveCharacterTextSplitter()
        chunks = text_splitter.split_documents(docs)
        self.retriever.add_documents(chunks,ids=None)
       
    def delete_index(self, index_name):
        self.pinecone.delete_index(index_name)

    def get_retriever(self):
        return self.retriever
    
    def query_vectors(self, vector, top_k=5):
        return self.index.query(vector=vector, top_k=top_k,include_values=True)

    def info(self):
        return self.index.describe_index_stats() # get some info on the index
    

if __name__ == '__main__':
    pinecone_api_key = "" # TODO: Paste API key here
    mistral_api_key = "" # TODO: Paste API Key here
    index_name = "actian"

    pinecone_manager = PineconeManager(pinecone_api_key=pinecone_api_key,mistral_api_key=mistral_api_key,index_name=index_name)
    pinecone_manager.add_data(documentPath="actian.txt")
    retriever = pinecone_manager.get_retriever()

    ################ CHAT SETUP ################

    model = ChatMistralAI(mistral_api_key=mistral_api_key) #https://python.langchain.com/docs/modules/model_io/llms/custom_llm/
    # prompt = ChatPromptTemplate.from_template("""If given context, answer the following question based only on the provided context:

    # <context>
    # {text}
    # </context>

    # Question: {input}""")                          
    contextualize_q_system_prompt = "You are a useful assistant called Doc Genie that answers in 100 words or less. Do NOT add any sources/links"
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
    )
    qa_system_prompt = """Reply in markdown format in 100 words or less. You must use bold text for important information. Do NOT add any sources/links. context:{context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # question classification model
    questionclassifier = QuestionClassifierDistilBERT()

    ################################################################################
    ############################# FRONT END (GRADIO) ###############################
    ################################################################################

    from PIL import Image
    image = Image.open("logo.png")

    css="""
    .message{
        background: white;
    }
    .message.user{
        border-left: 5px solid #51c8d2;
        padding: 20px 20px 20px 25px;
    }
    .message.bot{
        border-left: 5px solid #001e34;
        padding: 10px 10px 10px 25px;
    }
    #component-1{
        margin-top: -12px;
    }
    footer {visibility: hidden}
    .header{
        height: 9vh !important;
    }
    .chatbot {
        height: 68vh !important;
    }
    """
    with gr.Blocks(css=css) as demo:

        # Display logo and title above left panel
        with gr.Row(elem_classes = ["header"]):
            with gr.Column(scale=2):
                gr.Image(image, width=180, min_width=180, show_download_button=False, container=False)
            with gr.Column(scale=10):
                pass
        
        # Content / body
        with gr.Row():

            # Chatbot panel
            with gr.Column(scale=10):
                chatbot = gr.Chatbot(layout='panel', likeable="True", elem_classes=["chatbot"])
                with gr.Row(variant="compact"):
                    with gr.Column(scale=100):
                        msg = gr.Textbox(container="False", label="Enter a query about the documentation:")
                    
                    with gr.Column(scale=1, min_width=90, elem_classes=["text-input"]):
                        with gr.Row():
                            clear = gr.Button(min_width=40, size="sm", value="Clear Q/A")
                            enter = gr.Button(min_width=40, size="sm", value="Enter", elem_classes=["dark-button"])
                            
                history=[]
                def respond(message, chat_history):
                    output = {}
                    chat_history.append((message,""))

                    # single hop RAG
                    for chunk in rag_chain.stream({"input": message, "chat_history":history}):
                        for key in chunk:
                            if key not in output: output[key] = chunk[key]
                            else: output[key] += chunk[key]
                        if "answer" in output:
                            bot_message = output["answer"]
                            
                            # Append citation if exists
                            source_txt=''
                            if ("context" in output and len(output['context']) >= 1):
                                metadata = [doc.metadata for doc in output['context']]
                                source_txt = """\n\n```\nSources: {}\n```\n""".format(str(metadata))

                            chat_history[-1] = (message, bot_message + source_txt)
                            yield "", chat_history

                    # Obtain answer from RAG and append to history
                    history.extend([HumanMessage(content=message), bot_message])
                    chat_history.append((message, bot_message))
                    return "", chat_history
                    
                def clear_chatbot():
                    return "", []
                def clear_textbox():
                    return ""
                

                msg.submit(clear_textbox, [], [msg])
                msg.submit(respond, [msg, chatbot], [msg, chatbot])
                clear.click(clear_chatbot, [], [msg, chatbot])

    demo.launch()
