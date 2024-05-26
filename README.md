# MiniPilot

This application implements a chatbot you can train with your data. The example provided is a movie recommender system.

![demo](src/static/images/minipilot.gif)

The system uses:

- Redis Stack as a Vector Database to store the dataset and vectorize the entries to perform [Vector Similarity Search (VSS)](https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/) for RAG
- The [IMDB movies dataset](https://www.kaggle.com/datasets/ashpalsingh1525/imdb-movies-dataset), which contains 10000+ movies from the IMDB Movies dataset
- OpenAI ChatGPT Large Language Model (LLM) [ChatCompletion API](https://platform.openai.com/docs/guides/gpt/chat-completions-api)

## setup

Clone the repository 

```commandline
git clone https://github.com/mortensi/MiniPilot.git
```

Make sure you have an [OpenAI token](https://openai.com/api/pricing/), then install the requirements

```commandline
pip install -r requirements.txt
```

Then set the environment variables in a `.env` file.

```commandline
DB_SERVICE="127.0.0.1"
DB_PORT=6379
DB_PWD=""

MINIPILOT_DEBUG = "True"
MINIPILOT_MODEL="gpt-3.5-turbo-16k"

OPENAI_API_KEY="your-openai-key"
```

You can also use the `export` command.

```commandline
export DB_SERVICE="127.0.0.1" DB_PORT=6379 DB_PWD="" MINIPILOT_DEBUG = "True" MINIPILOT_MODEL="gpt-3.5-turbo-16k" OPENAI_API_KEY="your-openai-key"
```

Start the server `./start.sh`

Load the data with `python3 initialize.sh`

Point your browsert to `http://127.0.0.1:5005/` and start asking.

