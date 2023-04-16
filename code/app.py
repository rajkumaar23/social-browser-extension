from flask import Flask, jsonify, request, make_response
import pickle
import spacy
import json
from googlesearch import search
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
from time import sleep
from collections import Counter
from duckduckgo_search import ddg_news, ddg

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")


# pickle_filename = "dataset.pickle"
# with open(pickle_filename, "rb") as f:
#     dataset = pickle.load(f)

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def get_recommendations(urls):
    recommendations = []
    for url in urls:
        entities = []
        print("Processing " + url)
        response = requests.get(url)
        # soup = BeautifulSoup(response.content, 'html.parser')
        for entity in nlp(text_from_html(response.content)).ents:
            if entity.label_ in ['PERSON', 'ORG', 'GPE']:
                entity_text = ''.join(ch for ch in entity.text if ch.isalnum())
                if len(entity_text) > 2:
                    entities.append(entity_text)

        
        top_entities = [entity for entity, count in Counter(entities).most_common(10)]
        print("Entities for " + url + " found : " + json.dumps(top_entities))

        related_entities = []

        for entity in top_entities:
            entity = entity.lower().replace(" ", "_").replace("\n", "_")
            # Search for related entities in adjacent domains using ConceptNet API
            api_url = f"https://api.conceptnet.io/related/c/en/{entity}?filter=/c/en&limit=10"
            response = requests.get(api_url)
            print("Searching " + api_url)
            data = response.json()

            if not ('related' in data):
                continue

            related_entities += [item['@id'].split('/')[-1] for item in data['related'] if item['weight'] > 0.65]
            # print("Related : " + json.dumps(related_entities))

        top_related_entities = [entity for entity, count in Counter(related_entities).most_common(10)]
        print("Top related entities for " + url + " found : " + json.dumps(top_related_entities))

        for entity in related_entities:
            query = f"{entity}"
            # results = search('"' + query + '"', num_results=5, sleep_interval=1)
            response = ddg(query)
            # print(response)
            results = []
            if response is None or len(response) < 1:
                continue
            for item in response:
                if 'href' in item:
                    results.append({
                        'url': item['href'],
                        'title': item['title']
                    })
            i = 0
            for result in results:
                if i == 5:
                    break
                # print(result)
                if result['url'].count("/") > 3:
                    recommendations.append(result)
                    # print("Added " + result)
                    i += 1
            # print("Searched for " + entity)
            # print(recommendations)
        top_recommendations = [json.loads(recommendation) for recommendation, count in Counter(json.dumps(l) for l in recommendations).most_common(10)]
    print(top_recommendations)
    return top_recommendations

urls = ["https://paypal.com"]
# print(get_recommendations(urls))

@app.route("/recommendations", methods=["POST", "OPTIONS"])
def recommendations():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "POST":
        data = request.json
        urls = data["history"]
        recommendations = {
            'recommendations' : get_recommendations(urls)
        }
        return _corsify_actual_response(jsonify(recommendations))

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
