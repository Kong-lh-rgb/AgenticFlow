#对搜索到的数据进行向量化
from langchain_community.vectorstores import FAISS
from llm.llm_provider import embedding_models
from langchain_text_splitters import RecursiveCharacterTextSplitter
#文本分割
def text_splitter(text:str):
    """文本分割器"""
    docs = text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_splitter = text_splitter.split_text(docs)
    return all_splitter

def put_in_db(state:dict=None):
    """将文本放入向量数据库"""
    text = state["research_findings"]
    docs = text_splitter(text)
    embeddings = embedding_models
    vectorstore = FAISS.from_texts(
        texts=docs,
        embedding=embeddings,
    )
    return vectorstore

if __name__ == "__main__":
    sample_state = {
        "research_findings": """人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。AI技术包括机器学习、自然语言处理、计算机视觉等，广泛应用于医疗、金融、交通等领域。近年来，随着计算能力的提升和大数据的发展，AI技术取得了显著进展，推动了自动驾驶、智能助手等创新应用的发展。然而，AI的发展也带来了伦理和隐私等挑战，需要在技术进步的同时加以解决。"""
    }
    vector_db = put_in_db(sample_state)
    print(f"向量数据库包含 {vector_db.index.ntotal} 个向量。")