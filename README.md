# 🎮 Jogo Interativo de LIBRAS com Visão Computacional

## 📖 Visão Geral do Projeto

O projeto **Jogo Interativo de LIBRAS** (`jogo-libras`) é uma aplicação desenvolvida em Python que combina a **Linguagem Brasileira de Sinais (LIBRAS)** com tecnologias de **Visão Computacional** para criar uma experiência de aprendizado e interação gamificada.

O objetivo principal é permitir que o usuário interaja com um jogo (baseado em um *platformer* simples) utilizando gestos de LIBRAS capturados pela câmera, transformando a prática da linguagem de sinais em uma atividade divertida e engajadora.

## 🛠️ Tecnologias e Ferramentas

O projeto é construído sobre uma pilha de tecnologias Python, com foco em processamento de vídeo, detecção de poses e desenvolvimento de jogos.

| Categoria | Ferramenta | Versão Mínima | Descrição |
| :--- | :--- | :--- | :--- |
| **Desenvolvimento de Jogos** | `pygame` | `2.5.0` | Biblioteca principal para a criação do jogo e sua interface gráfica. |
| **Detecção de Gestos/Poses** | `mediapipe` | `0.10.0` | Utilizado para a detecção de pontos-chave (landmarks) das mãos e do corpo, essenciais para o reconhecimento dos sinais de LIBRAS. |
| **Processamento de Vídeo** | `opencv-python` | `4.8.0` | Responsável pela captura e processamento do *feed* da câmera em tempo real. |
| **Processamento Numérico** | `numpy` | `1.24.0` | Essencial para operações matemáticas e manipulação eficiente de dados de coordenadas e vetores. |
| **Processamento de Imagens** | `Pillow` | `10.0.0` | Utilizado para manipulação e carregamento de ativos de imagem no jogo. |
| **Visualização (Opcional)** | `matplotlib` | `3.7.0` | Pode ser usado para visualização de dados e *debugging* do modelo de reconhecimento. |

## 📂 Estrutura do Repositório

A estrutura do projeto é modular, separando as responsabilidades de coleta de dados, carregamento de modelos, identificação de sinais e a lógica principal do jogo.

```
jogo-libras/
├── candango_game.py
├── libras_data_collector.py
├── libras_dataset.csv
├── libras_model_loader.py
├── libras_sign_identifier.py
├── requirements.txt
└── README.md
```

| Arquivo | Descrição |
| :--- | :--- |
| `candango_game.py` | Contém a lógica principal do jogo (baseado na classe `PlatformGame`), integrando a interface Pygame com o sistema de reconhecimento de sinais. |
| `libras_data_collector.py` | Script dedicado à coleta de dados de gestos de LIBRAS, utilizando o MediaPipe para extrair *landmarks* e salvar no arquivo de dataset. |
| `libras_dataset.csv` | O dataset de treinamento, armazenando as coordenadas dos *landmarks* de cada sinal de LIBRAS coletado. |
| `libras_model_loader.py` | Responsável por carregar ou treinar o modelo de Machine Learning que fará a classificação dos sinais com base nos dados do `libras_dataset.csv`. |
| `libras_sign_identifier.py` | Módulo que encapsula a lógica de identificação de sinais em tempo real, recebendo o *frame* da câmera e retornando o sinal de LIBRAS detectado. |
| `requirements.txt` | Lista todas as dependências Python necessárias para o projeto. |

## ⚙️ Funcionalidades Principais

O projeto é dividido em duas grandes áreas de funcionalidade: a **Coleta e Treinamento do Modelo** e a **Execução do Jogo**.

### 1. Coleta e Treinamento do Modelo

*   **Coleta de Dados:** O script `libras_data_collector.py` utiliza o MediaPipe para capturar as coordenadas 3D dos *landmarks* das mãos e do corpo do usuário enquanto ele executa os sinais de LIBRAS. Esses dados são serializados e armazenados no `libras_dataset.csv`.
*   **Treinamento do Modelo:** O módulo `libras_model_loader.py` é responsável por:
    *   Ler o `libras_dataset.csv`.
    *   Processar os dados (normalização, extração de características).
    *   Treinar um modelo de classificação (provavelmente um classificador baseado em vetores de características, como SVM ou Random Forest) para reconhecer os sinais.
    *   Salvar o modelo treinado para uso posterior.

### 2. Execução do Jogo

*   **Integração com Câmera:** O `libras_sign_identifier.py` utiliza o OpenCV para acessar a câmera e o MediaPipe para processar o *frame* em tempo real.
*   **Reconhecimento em Tempo Real:** O módulo identifica o sinal de LIBRAS que está sendo executado pelo usuário, utilizando o modelo carregado.
*   **Controle do Jogo:** O `candango_game.py` recebe o sinal de LIBRAS identificado e o mapeia para uma ação do jogo (ex: sinal de "pular" -> personagem pula).
*   **Mecânica de Jogo:** O jogo é um *platformer* simples, onde a interação do usuário é feita exclusivamente através dos sinais de LIBRAS.

## 🚀 Como Executar

Para configurar e rodar o projeto, siga os passos abaixo:

### Pré-requisitos

*   Python 3.x
*   Câmera web funcional

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/LeoSousaJesus/jogo-libras.git
    cd jogo-libras
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Uso

1.  **Coletar/Treinar o Modelo (Se necessário):**
    *   Se você precisar adicionar novos sinais ou retreinar o modelo, execute o coletor de dados:
        ```bash
        python libras_data_collector.py
        ```
    *   Em seguida, execute o carregador/treinador do modelo:
        ```bash
        python libras_model_loader.py
        ```

2.  **Rodar o Jogo:**
    *   Execute o arquivo principal do jogo:
        ```bash
        python candango_game.py
        ```
    *   A câmera será ativada, e você poderá interagir com o jogo usando os sinais de LIBRAS.


## 📄 Licença

Este projeto está sob a licença [MIT](https://choosealicense.com/licenses/mit/).