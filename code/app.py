from flask import Flask, jsonify, request, make_response
import spacy
import json
from googlesearch import search
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
from time import sleep
from collections import Counter

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def get_title_and_image(url):
    try:
        response = requests.get(url)
    except:
        return (None, None)
    soup = BeautifulSoup(response.content, 'html.parser')
    if response.status_code != 200 or soup.title == None:
        return (None, None)
    title = soup.title.string
    image = soup.find("meta", property="og:image")
    return (title, image['content'] if image else 'https://placehold.co/100x55')


def get_recommendations(urls):
    recommendations = []
    for url in urls:
        entities = []
        print("Processing " + url)
        response = requests.get(url)
        for entity in nlp(text_from_html(response.content)).ents:
            if entity.label_ in ['PERSON', 'ORG', 'GPE']:
                entity_text = ''.join(ch for ch in entity.text if ch.isalnum())
                if len(entity_text) > 2:
                    entities.append(entity_text)

        top_entities = [entity for entity, count in Counter(entities).most_common(20)]
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

            related_entities += [item['@id'].split('/')[-1]
                                 for item in data['related'] if item['weight'] > 0.5][:3]
            # print("Related : " + json.dumps(related_entities))

        top_related_entities = [entity for entity, count in Counter(
            related_entities).most_common(5)]
        print("Top related entities for " + url +
              " found : " + json.dumps(top_related_entities))

        for entity in top_related_entities:
            results = []
            for result in search(entity + ' News', num=10, stop=1, pause=2, extra_params={'tbm': 'nws'}):
                if result.count("/") > 3:
                    title, image = get_title_and_image(result)
                    if title == None:
                        continue
                    recommendations.append({
                        'url': result,
                        'title': title,
                        'image': image
                    })
            print("Searched for " + entity)
        top_recommendations = [json.loads(recommendation) for recommendation, count in Counter(
            json.dumps(l) for l in recommendations).most_common(20)]
    print(top_recommendations)
    return top_recommendations


@app.route("/recommendations", methods=["POST", "OPTIONS"])
def recommendations():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "POST":
        data = request.json
        urls = data["history"]
        recommendations = {
            'recommendations': get_recommendations(urls)
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

app.run(host='0.0.0.0', port=9050)