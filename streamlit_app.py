import streamlit as st
from difflib import SequenceMatcher
from typing import List, Set, Tuple
import pandas as pd


st.set_page_config(
    page_title="Separador de Palavras",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="expanded"
)
class SimilarityGrouper:
    def __init__(self, similarity_threshold: float = 0.8, min_similar_words: int = 2):
        self.similarity_threshold = similarity_threshold
        self.min_similar_words = min_similar_words

    def calculate_similarity(self, word1: str, word2: str) -> float:
        """Calcula a similaridade entre duas palavras."""
        word1, word2 = word1.lower(), word2.lower()
        return SequenceMatcher(None, word1, word2).ratio()

    def get_similar_words_count(self, phrase1: str, phrase2: str) -> int:
        """Conta quantas palavras similares existem entre duas frases."""
        words1 = phrase1.lower().split()
        words2 = phrase2.lower().split()
        
        similar_pairs = []
        for w1 in words1:
            for w2 in words2:
                if (w1, w2) not in similar_pairs and (w2, w1) not in similar_pairs:
                    if self.calculate_similarity(w1, w2) > self.similarity_threshold:
                        similar_pairs.append((w1, w2))
        
        return len(similar_pairs)

    def are_phrases_similar(self, phrase1: str, phrase2: str) -> bool:
        """Verifica se duas frases são similares baseado no número de palavras similares."""
        similar_count = self.get_similar_words_count(phrase1, phrase2)
        return similar_count >= self.min_similar_words

    def extract_keywords(self, phrase: str) -> Set[str]:
        """Extrai palavras-chave de uma frase, excluindo palavras repetidas."""
        words = set(phrase.lower().split())  # Usa set para excluir palavras duplicadas
        return words

    def group_similar_phrases(self, phrases: List[str]) -> List[Tuple[Set[str], List[str]]]:
        """Agrupa frases similares e retorna grupos com suas palavras-chave."""
        groups = []  # Lista de tuplas (palavras-chave, lista_de_frases)
        
        for phrase in phrases:
            best_match = None
            best_match_score = 0
            
            # Procura o melhor grupo para a frase atual
            for idx, (keywords, group_phrases) in enumerate(groups):
                total_similarity = sum(
                    self.get_similar_words_count(phrase, group_phrase)
                    for group_phrase in group_phrases
                )
                average_similarity = total_similarity / len(group_phrases)
                
                if average_similarity >= self.min_similar_words and average_similarity > best_match_score:
                    best_match = idx
                    best_match_score = average_similarity
            
            if best_match is not None:
                # Adiciona a frase ao melhor grupo encontrado
                keywords, group_phrases = groups[best_match]
                keywords.update(self.extract_keywords(phrase))
                group_phrases.append(phrase)
            else:
                # Cria um novo grupo
                groups.append((self.extract_keywords(phrase), [phrase]))
        
        return groups

# Função principal do Streamlit
def main():
    st.title("Agrupamento de Frases por Similaridade")

    # Upload do arquivo de texto
    uploaded_file = st.sidebar.file_uploader("Escolha um arquivo de texto", type=["txt"])

    if uploaded_file is not None:
        # Lê o conteúdo do arquivo
        file_content = uploaded_file.getvalue().decode("utf-8")
        phrases = [line.strip() for line in file_content.splitlines() if line.strip()]

        # Exclui frases com palavras exatamente iguais
        phrases = list(pd.Series(phrases).drop_duplicates().values)

        # # Exibe as frases carregadas
        # st.write("Frases carregadas:")
        # st.text(file_content)

        # Definindo os parâmetros de similaridade
        similarity_threshold = st.slider("Limiar de Similaridade", 0.0, 1.0, 0.8)
        min_similar_words = st.slider("Número Mínimo de Palavras Similares", 1, 5, 2)

        # Agrupando as frases por similaridade
        grouper = SimilarityGrouper(similarity_threshold, min_similar_words)
        groups = grouper.group_similar_phrases(phrases)

        # Exibindo os resultados
        st.write("Resultados do Agrupamento:")

        result_str = ""  # String para armazenar os resultados formatados
        for keywords, grouped_phrases in groups:
            group_str = f"**Grupo de Similaridade baseado em:** {', '.join(sorted(keywords))}\n"
            for phrase in grouped_phrases:
                group_str += f"  - {phrase}\n"
            group_str += "\n"
            result_str += group_str
            st.write(group_str)

        # Botão de download
        st.sidebar.download_button(
            label="Baixar Resultados como .txt",
            data=result_str,
            file_name="resultados_agrupados.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
