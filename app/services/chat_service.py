from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.core.settings import settings


class Chat:
    def __init__(self):
        self.chat_model = ChatGoogleGenerativeAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            api_key=settings.LLM_API_KEY
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.chat_histories: dict[str, list] = {}

    def get_chat_response(self, question: str, collection_name: str) -> tuple[str, list]:
        """Get chat response based on question and chat history."""

        # Load chat history or initialize if not present
        chat_history = self.chat_histories.get(collection_name, [])

        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.data.vector_store_dir
        )
        
        retriever = vector_store.as_retriever()

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
            "input": question
        })

        # Update chat history
        chat_history.append(HumanMessage(content=question))
        chat_history.append(AIMessage(content=response["answer"]))

        # Save history back
        self.chat_histories[collection_name] = chat_history

        return response["answer"], [msg.content for msg in chat_history]
