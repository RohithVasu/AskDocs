from loguru import logger
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_qdrant import QdrantVectorStore
from langchain.retrievers import EnsembleRetriever

from app.core.db import get_global_db_session_ctx
from app.core.llm import llm
from app.core.settings import settings
from app.core.qdrant import Qdrant
from app.model_handlers.chat_message_handler import ChatMessageHandler
from app.model_handlers.chat_session_documents_handler import ChatSessionDocumentHandler
from app.model_handlers.document_handler import DocumentHandler


class Chat:
    def __init__(self):
        self.chat_model = llm
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.qdrant = Qdrant()

    def get_collection_names(self, session_id: str) -> list:
        with get_global_db_session_ctx() as db:
            chat_session_document_handler = ChatSessionDocumentHandler(db)
            documents = chat_session_document_handler.get_by_session(session_id)
            doc_ids = [doc.document_id for doc in documents]

            collection_names = []
            document_handler = DocumentHandler(db)
            for doc_id in doc_ids:
                doc = document_handler.read(doc_id)
                collection_names.append(doc.vector_collection)
            return collection_names

    def get_chat_history(self, session_id: str) -> list:
        chat_history = []
        with get_global_db_session_ctx() as db:
            chat_message_handler = ChatMessageHandler(db)
            messages = chat_message_handler.get_by_session(session_id)

            for message in messages:
                chat_history.append(HumanMessage(content=message.query))
                chat_history.append(AIMessage(content=message.response))
            return chat_history

    def get_chat_response(self, session_id: str, query: str) -> str:
        """Get chat response based on question and chat history."""

        # Load chat history or initialize if not present
        chat_history = self.get_chat_history(session_id)

        collections = self.get_collection_names(session_id)

        if len(collections) == 0:
            raise ValueError("No documents found for session")

        retrievers = []
        for collection in collections:
            vs = QdrantVectorStore(
                client=self.qdrant.client,
                collection_name=collection,
                embedding=self.embeddings
            )
            retrievers.append(vs.as_retriever(search_kwargs={"k": settings.qdrant.search_limit}))

        weights = [1.0 / len(retrievers)] * len(retrievers)

        ensemble_retriever = EnsembleRetriever(
            retrievers=retrievers,
            weights=weights
        )
        
        contextualize_q_prompt  = ChatPromptTemplate.from_messages(
            [
                ("system", settings.llm.retriever_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        
        history_aware_retriever = create_history_aware_retriever(
            self.chat_model,
            ensemble_retriever,
            contextualize_q_prompt
        )

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", settings.llm.system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(self.chat_model, qa_prompt)
        
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        response = rag_chain.invoke({
            "chat_history": chat_history,
            "input": query
        })

        return response["answer"]
