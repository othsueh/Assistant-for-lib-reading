from langchain_core.documents import Document
from langchain.text_splitter import RecursiveJsonSplitter, MarkdownTextSplitter
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import json
import os
from dotenv import load_dotenv


class CodeAssistant:
    def __init__(self, json_path, markdown_dir=None, model="claude-3-sonnet-20240229", load_faiss_from=None):
        load_dotenv()
        self.model = ChatAnthropic(
            model=model,
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            max_tokens=4096,
        )
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        self.dialogs = {}
        if load_faiss_from and os.path.exists(load_faiss_from):
            # Load existing FAISS index
            print(f"Loading existing FAISS index from {load_faiss_from}")
            self.vectorstore = self.load_faiss(load_faiss_from)
        else:
            # Process documents and create new FAISS index
            print("Creating new FAISS index...")
            # Load and process JSON data
            self.json_docs = self.process_json(json_path)
            
            # Load and process Markdown files if provided
            self.markdown_docs = []
            if markdown_dir:
                self.markdown_docs = self.process_markdown(markdown_dir)
                
            # Combine all documents
            all_docs = self.json_docs + self.markdown_docs
            
            # Create vector store
            self.vectorstore = FAISS.from_documents(all_docs, self.embeddings)

    def save_faiss(self, save_path):
        """Save FAISS index to disk"""
        self.vectorstore.save_local(save_path)
        print(f"FAISS index saved to {save_path}")
    
    def load_faiss(self, load_path):
        """Load FAISS index from disk"""
        return FAISS.load_local(load_path, self.embeddings,allow_dangerous_deserialization=True)
        
    def process_json(self, json_path):
        """Process JSON file into documents"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Configure JSON splitter
        json_splitter = RecursiveJsonSplitter(
            max_chunk_size=1000,
        )
        
        def process_file(file_data):
            """Process individual file data"""
            documents = []
            
            # For Python files
            if file_data.get("type") == "python":
                # Process classes
                for class_info in file_data.get("classes", []):
                    class_text = f"""
                    File: {file_data['file_name']}
                    Class: {class_info['name']}
                    Decorators: {', '.join(class_info['decorators'])}
                    Inherits: {', '.join(class_info['inherits'])}
                    Methods: {', '.join(m['name'] for m in class_info['methods'])}
                    """
                    documents.append(Document(
                        page_content=class_text,
                        metadata={
                            "file_name": file_data['file_name'],
                            "type": "class",
                            "class_name": class_info['name']
                        }
                    ))
                    
                    # Process methods
                    for method in class_info['methods']:
                        method_text = f"""
                        File: {file_data['file_name']}
                        Class: {class_info['name']}
                        Method: {method['name']}
                        Decorators: {', '.join(method['decorators'])}
                        Body: {method['body']}
                        """
                        documents.append(Document(
                            page_content=method_text,
                            metadata={
                                "file_name": file_data['file_name'],
                                "type": "method",
                                "class_name": class_info['name'],
                                "method_name": method['name']
                            }
                        ))
                
                # Process standalone functions
                for func in file_data.get("other_functions", []):
                    func_text = f"""
                    File: {file_data['file_name']}
                    Function: {func['name']}
                    Decorators: {', '.join(func['decorators'])}
                    Body: {func['body']}
                    """
                    documents.append(Document(
                        page_content=func_text,
                        metadata={
                            "file_name": file_data['file_name'],
                            "type": "function",
                            "function_name": func['name']
                        }
                    ))
            
            # For YAML files
            elif file_data.get("type") == "yaml":
                yaml_text = f"""
                File: {file_data['file_name']}
                Content: {json.dumps(file_data['content'], indent=2)}
                """
                documents.append(Document(
                    page_content=yaml_text,
                    metadata={
                        "file_name": file_data['file_name'],
                        "type": "yaml"
                    }
                ))
                
            return documents
        
        def traverse_directory(directory_data):
            """Recursively traverse directory structure"""
            documents = []
            
            # Process files in current directory
            for file_data in directory_data.get("files", []):
                documents.extend(process_file(file_data))
                
            # Process subdirectories
            for subdir in directory_data.get("subdirs", []):
                documents.extend(traverse_directory(subdir))
                
            return documents
        
        # Process entire directory structure
        return traverse_directory(data)
    
    def process_markdown(self, markdown_dir):
        """Process markdown files into documents"""
        markdown_splitter = MarkdownTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        documents = []
        for filename in os.listdir(markdown_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(markdown_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                md_docs = markdown_splitter.create_documents(
                    [content],
                    metadatas=[{
                        "file_name": filename,
                        "type": "markdown"
                    }]
                )
                documents.extend(md_docs)
                
        return documents
    
    def get_relevant_context(self, query, k=5):
        """Retrieve relevant context for the query"""
        return self.vectorstore.similarity_search(query, k=k)
    
    def chat(self, query, system_prompt=None, dialog_id="default"):
        """Chat with the assistant using RAG"""
        # Initialize dialog history if it doesn't exist
        if dialog_id not in self.dialogs:
            self.dialogs[dialog_id] = []
            
        # Use dialog-specific history
        conversation_history = self.dialogs[dialog_id]

        # Get relevant context
        # context_docs = self.get_relevant_context(query)
        # context = "\n\n".join([doc.page_content for doc in context_docs])
        
        # Prepare system prompt
        # if system_prompt is None:
        #     system_prompt = """You are a helpful coding assistant with knowledge about a specific codebase. 
        #     Use the provided context to answer questions about the code, but don't make assumptions beyond what's shown. 
        #     If you're unsure about something, say so."""
        
        # Use minimal system prompt for testing
        system_prompt = "You are a test assistant. Reply with short responses."

        # Prepare messages with conversation history
        messages = [
            {"role": "system", "content": system_prompt},
            # {"role": "user", "content": f"Context about the codebase:\n{context}"}
        ]
        
        # Add dialog-specific conversation history instead of self.conversation_history
        messages.extend(conversation_history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        # Get response
        response = self.model.invoke(messages)
        
        # Save the interaction to dialog-specific history instead of self.conversation_history
        self.dialogs[dialog_id].extend([
            {"role": "user", "content": query},
            {"role": "assistant", "content": response.content}
        ])
        
        return response.content

    async def chat_stream(self, query, system_prompt=None, dialog_id="default"):
        """Streaming chat with the assistant using RAG"""
        try:
            if dialog_id not in self.dialogs:
                self.dialogs[dialog_id] = []
                    
            conversation_history = self.dialogs[dialog_id]
            context_docs = self.get_relevant_context(query)
            context = "\n\n".join([doc.page_content for doc in context_docs])
                
            if system_prompt is None:
                system_prompt = """You are a helpful coding assistant..."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context about the codebase:\n{context}"}
            ]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": query})
                
            # Get streaming response
            async for chunk in self.model.astream(messages):  # Use astream instead of stream
                if chunk.content:
                    yield chunk.content
            
        except Exception as e:
            print(f"Stream error in assistant: {str(e)}")
            raise

def load_system_prompt(file_path="system_prompt.txt"):
    """Load system prompt from file, or return default if file doesn't exist"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Using default system prompt.")
        return """You are a cute cat who alwyas meows and purrs."""

# Example usage:
if __name__ == "__main__":
    assistant = CodeAssistant(
        json_path="project_structure.json",
        markdown_dir="../ellama_codebase/",
        model="claude-3-sonnet-20240229",
        load_faiss_from="project_faiss"
    )
    # Save FAISS index if it was newly created
    if not os.path.exists("project_faiss"):
        assistant.save_faiss("project_faiss")
    # Example system prompt
    system_prompt = load_system_prompt()
    
    # Example chat
    while True:
        query = input("\nEnter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
            
        response = assistant.chat(query, system_prompt)
        print("\nAssistant:", response)