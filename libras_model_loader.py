import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

class LibrasModelLoader:
    def __init__(self, model_path='libras_dataset.csv'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        if not os.path.exists(self.model_path):
            print(f"Erro: Arquivo de modelo não encontrado em {self.model_path}")
            return
        try:
            df = pd.read_csv(self.model_path)
            X = df.drop('label', axis=1)
            y = df['label']

            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Usar um modelo simples como KNN para demonstração
            self.model = KNeighborsClassifier(n_neighbors=5)
            self.model.fit(X_scaled, y)
            print("Modelo de Libras carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar o modelo de Libras: {e}")
            self.model = None

    def predict(self, hand_landmarks_flat: list) -> str:
        if self.model is None or self.scaler is None:
            return "MODELO_NAO_CARREGADO"
        try:
            # Converter landmarks para o formato esperado pelo modelo
            # Certifique-se de que a ordem e o número de landmarks correspondam ao treinamento
            input_data = np.array(hand_landmarks_flat).reshape(1, -1)
            input_scaled = self.scaler.transform(input_data)
            prediction = self.model.predict(input_scaled)
            return str(prediction[0])
        except Exception as e:
            # print(f"Erro ao prever letra de Libras: {e}") # Para debug
            return "FORMATO_INCORRETO"

if __name__ == '__main__':
    # Exemplo de uso e teste do carregador de modelo
    # Certifique-se de ter um libras_dataset.csv válido para testar
    model_loader = LibrasModelLoader()
    if model_loader.model:
        print("Modelo pronto para uso.")
        # Exemplo de landmarks (substitua por dados reais)
        dummy_landmarks = [0.5] * 63 # 21 landmarks * 3 coordenadas (x,y,z)
        predicted_letter = model_loader.predict(dummy_landmarks)
        print(f"Letra prevista: {predicted_letter}")
    else:
        print("Falha ao carregar o modelo.")


