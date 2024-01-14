# Standard library imports
import os
import logging
import csv
import json

# Third party imports
from dotenv import load_dotenv
import requests
import boto3
from flask import Flask, request, render_template, jsonify

# Local application/library specific imports
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import BedrockEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.llms.bedrock import Bedrock

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
app = Flask(__name__)

# AWS credentials for Bedrock
aws_region = os.environ.get("AWS_REGION")

# ServiceNow credentials and instance
snow_client_id = os.environ.get("SNOW_CLIENT_ID")
snow_client_secret = os.environ.get("SNOW_CLIENT_SECRET")
snow_user = os.environ.get("SNOW_USER")
snow_password = os.environ.get("SNOW_PASSWORD")
snow_instance = os.environ.get("SNOW_INSTANCE")

# Validate environment variables
if not all(
    [
        aws_region,
        snow_client_id,
        snow_client_secret,
        snow_user,
        snow_password,
        snow_instance,
    ]
):
    logging.error("Missing required environment variables.")
    exit(1)

# Setup Bedrock runtime client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=aws_region,
)


class ServiceNowAPI:
    def __init__(self, client_id, client_secret, user, password, instance):
        self.token_url = f"https://{instance}.service-now.com/oauth_token.do"
        self.api_url = f"https://{instance}.service-now.com/api/now/table/incident"
        self.client_id = client_id
        self.client_secret = client_secret
        self.user = user
        self.password = password

    def get_oauth_token(self):
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.user,
            "password": self.password,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_incidents(self, token):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.get(self.api_url, headers=headers)
        response.raise_for_status()
        return response.json()["result"]

    def export_incidents_to_csv(self, filename="servicenow_incidents.csv"):
        try:
            token = self.get_oauth_token()
            incidents = self.get_incidents(token)
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=incidents[0].keys())
                writer.writeheader()
                for incident in incidents:
                    writer.writerow(incident)
            logging.info(f"Incidents exported to {filename}")
        except requests.HTTPError as e:
            logging.error(f"HTTP error occurred: {e.response.text}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


class QnABot:
    def __init__(self, csv_file):
        self.csv_file = csv_file

    def setup_bot(self):
        loader = CSVLoader(self.csv_file)
        documents = loader.load()
        embedding_function = BedrockEmbeddings(
            client=bedrock_runtime,
            model_id="amazon.titan-embed-text-v1",
        )
        db = Chroma.from_documents(documents, embedding_function)
        retriever = db.as_retriever()

        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)

        model = Bedrock(client=bedrock_runtime, model_id="anthropic.claude-v2")
        model.model_kwargs = {"temperature": 0.7, "max_tokens_to_sample": 2048}

        self.chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )

    def ask_question(self, question):
        try:
            return self.chain.invoke(question)
        except Exception as e:
            logging.error(f"Error in asking question: {e}")
            return None


try:
    # Initialize ServiceNow API and export incidents to CSV
    service_now_api = ServiceNowAPI(
        snow_client_id, snow_client_secret, snow_user, snow_password, snow_instance
    )
    service_now_api.export_incidents_to_csv()

    # Initialize and setup Q&A Bot
    qna_bot = QnABot("servicenow_incidents.csv")
    qna_bot.setup_bot()
except Exception as e:
    logging.error(f"Failed to initialize services: {e}")
    exit(1)


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        question = data.get("question")
        question = question.strip()

        if not question:
            return jsonify({"error": "Please enter your question."})

        # Check for specific inputs and provide custom responses
        if question.lower() in ["thank you", "thanks", "thank you!"]:
            return jsonify({"answer": "You're welcome!"})

        if question.lower() in ["bye", "exit", "stop", "end"]:
            return jsonify({"answer": "Goodbye!"})

        ai_response = qna_bot.ask_question(question)
        if ai_response:
            return jsonify({"answer": ai_response})
        else:
            return jsonify({"answer": "Unable to get an answer."})

    except Exception as e:
        logging.error(f"Failed to process question: {e}")
        return jsonify({"error": "An error occurred while processing your question."})


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run()
