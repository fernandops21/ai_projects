# ai_projects

Experimentos com IA rodando localmente, usando o modelo **Mistral 7B** via [Ollama](https://ollama.com).

## Estrutura

| Pasta | Descrição |
|---|---|
| [`learning/`](learning/) | Primeiros experimentos: chat no terminal e interface web simples (Gradio) |
| [`personal_ai/`](personal_ai/) | Assistente pessoal que aprende sobre o usuário com 4 sistemas de memória (working, episodic, semantic, procedural) |

## Pré-requisitos

- Python 3.12
- Ollama instalado, com o modelo baixado: `ollama pull mistral:7b`

## Como rodar o `personal_ai`

```bash
cd personal_ai
python -m venv personal-ai-venv
source personal-ai-venv/bin/activate
pip install -r requirements.txt
python app.py
```

A interface abre em http://127.0.0.1:7860. As memórias ficam salvas localmente em `personal_ai/data/` (fora do git).
