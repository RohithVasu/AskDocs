from loguru import logger
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from qdrant_client import models

from app.core.db import get_global_db_session_ctx
from app.core.llm import llm
from app.core.settings import settings
from app.core.qdrant import get_qdrant_client
from app.model_handlers.chat_message_handler import ChatMessageHandler
from app.model_handlers.chat_session_documents_handler import ChatSessionDocumentHandler
from app.model_handlers.document_handler import DocumentHandler

class Chat:
    def __init__(self):
        self.chat_model = llm
        self.qdrant = get_qdrant_client()

    def get_document_names(self, session_id: str) -> list:
        with get_global_db_session_ctx() as db:
            chat_session_document_handler = ChatSessionDocumentHandler(db)
            documents = chat_session_document_handler.get_by_session(session_id)
            doc_ids = [doc.document_id for doc in documents]

            document_names = []
            document_handler = DocumentHandler(db)
            for doc_id in doc_ids:
                doc = document_handler.read(doc_id)
                document_names.append(doc.filename)
            return document_names

    def get_chat_history(self, session_id: str) -> list:
        chat_history = []
        with get_global_db_session_ctx() as db:
            chat_message_handler = ChatMessageHandler(db)
            messages = chat_message_handler.get_by_session(session_id)

            for message in messages:
                chat_history.append(HumanMessage(content=message.query))
                chat_history.append(AIMessage(content=message.response))
            return chat_history

    def get_chat_response(self, user_id: str, session_id: str, query: str) -> str:
        """Get chat response based on question and chat history."""

        # Load chat history or initialize if not present
        chat_history = self.get_chat_history(session_id)

        document_names = self.get_document_names(session_id)

        if len(document_names) == 0:
            raise ValueError("No documents found for session")

        vector_store = self.qdrant._get_vector_store(collection_name=user_id)

        # Build filter for a list of documents (sources)
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.source",
                    match=models.MatchAny(any=document_names)
                )
            ]
        )

        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": settings.qdrant.search_limit,
                "filter": filter_condition,
            }
        )
        # retriever = vector_store.as_retriever(search_kwargs={"k": settings.qdrant.search_limit})
        
        contextualize_q_prompt  = ChatPromptTemplate.from_messages(
            [
                ("system", settings.llm.retriever_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        
        history_aware_retriever = create_history_aware_retriever(
            self.chat_model,
            retriever,
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

    def stream_chat_response(self, user_id: str, session_id: str, query: str):
        """Stream chat response based on question and chat history."""

        # Load chat history or initialize if not present
        chat_history = self.get_chat_history(session_id)

        document_names = self.get_document_names(session_id)

        if len(document_names) == 0:
            raise ValueError("No documents found for session")

        vector_store = self.qdrant._get_vector_store(collection_name=user_id)

        # Build filter for a list of documents (sources)
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.source",
                    match=models.MatchAny(any=document_names)
                )
            ]
        )

        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": settings.qdrant.search_limit,
                "filter": filter_condition,
            }
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
            retriever,
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

        for chunk in rag_chain.stream({
            "chat_history": chat_history,
            "input": query
        }):
            if "answer" in chunk:
                yield chunk["answer"]
