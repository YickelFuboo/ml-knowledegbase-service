import nltk
import logging

logging.basicConfig(level=logging.INFO)

def ensure_nltk_data():
    """确保 NLTK 数据已下载"""
    punkt_available = False
    try:
        nltk.data.find('tokenizers/punkt_tab')
        punkt_available = True
        logging.info("NLTK punkt_tab 数据已存在")
    except LookupError:
        try:
            nltk.data.find('tokenizers/punkt')
            punkt_available = True
            logging.info("NLTK punkt 数据已存在")
        except LookupError:
            pass
    
    if not punkt_available:
        logging.info("正在下载 NLTK punkt_tab 数据...")
        try:
            nltk.download('punkt_tab', quiet=True)
            logging.info("NLTK punkt_tab 数据下载完成")
        except Exception:
            try:
                nltk.download('punkt', quiet=True)
                logging.info("NLTK punkt 数据下载完成")
            except Exception as e:
                logging.warning(f"下载 NLTK punkt 数据失败: {e}")
    
    try:
        nltk.data.find('corpora/wordnet')
        logging.info("NLTK wordnet 数据已存在")
    except LookupError:
        logging.info("正在下载 NLTK wordnet 数据...")
        nltk.download('wordnet', quiet=True)
        logging.info("NLTK wordnet 数据下载完成")
    
    try:
        nltk.data.find('corpora/omw-1.4')
        logging.info("NLTK omw-1.4 数据已存在")
    except LookupError:
        try:
            logging.info("正在下载 NLTK omw-1.4 数据...")
            nltk.download('omw-1.4', quiet=True)
            logging.info("NLTK omw-1.4 数据下载完成")
        except Exception as e:
            logging.warning(f"下载 NLTK omw-1.4 数据失败: {e}")

if __name__ == "__main__":
    ensure_nltk_data()
