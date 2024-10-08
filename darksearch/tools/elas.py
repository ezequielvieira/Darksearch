#!/usr/bin/python

import os
import pandas as pd
import json
import requests
import re
import gc
from elasticsearch import Elasticsearch

# Adicione suas credenciais de autenticação aqui
es = Elasticsearch(
    hosts=["https://150c57661e174c5e910932c24665a833.southamerica-east1.gcp.elastic-cloud.com:443"],
    http_auth=("elastic", "k2W8gl8D9xi1SGVy592aZG31")  # Substitua "seu_usuario" e "sua_senha" pelas suas credenciais
)

class DarkElastic(object):

    def __init__(self):
        self.size = 0
        self.briefList = []
        self.titleList = []
        self.namesList = []
        self.datesList = []

    def pandas_to_json(self, jsonPath):
        """
        Take logFile, open as Dataframe, convert to JSON, Save JSON.
        """
        self.jsonPath = jsonPath
        self.logPath = os.getcwd()+'/../logs/process2.csv'
        with open(self.logPath) as logs:
            searchIndex = pd.read_csv(
                logs,
                header=None,
                sep='\t',
                names=[
                    "DATES",
                    "URLS",
                    "NAMES",
                    "SIZE",
                    "LANG",
                    "TITLE",
                    "CONTENT"
                ]
            )
        self.size = len(searchIndex.index)
        searchIndex = searchIndex.to_json(orient='index')
        searchIndex = json.loads(searchIndex)
        self.searchIndex = searchIndex
        self.save_json(searchIndex)

    def save_json(self, dataframe):
        with open(self.jsonPath, "w") as outfile:
            json.dump(dataframe, outfile, indent=4)
        print('Dataframe converted to JSON.')

    def ingest_items(self):
        for i in range(0, self.size):
            doc = self.searchIndex[str(i)]
            res = es.index(
                index="dark",
                doc_type='html',
                id=i,
                body=doc
            )
            print('Ingested document %d...' % i)
        return res['result'] == 'created'

    def get_items(self, i):
        res = es.get(
            index="dark",
            doc_type='html',
            id=i
        )
        return res['_source']

    def search_index(self, myIndex, myQuery, start=0, end=10):
        # Verifique se o índice existe
        if not es.indices.exists(index=myIndex):
            print(f"Índice '{myIndex}' não encontrado. Criando índice...")
            es.indices.create(index=myIndex)

        res = es.search(
            index=myIndex,
            body={
                "from": start,
                "size": end,
                'query': {
                    "query_string": {
                        "default_field": "CONTENT",
                        "query": myQuery
                    }
                },
                "sort": {
                    "_score": {
                        "order": "desc"
                    }
                }
            }
        )
        self.size = res['hits']['total']['value']
        self.briefList = [hit['_source']['CONTENT'] for hit in res['hits']['hits']]
        self.titleList = [hit['_source']['TITLE'] for hit in res['hits']['hits']]
        self.namesList = [hit['_source']['NAMES'] for hit in res['hits']['hits']]
        self.datesList = [hit['_source']['DATES'] for hit in res['hits']['hits']]
        return res

    def check_cat(self, val):
        """
        Check category of the result.
        """
        return "category"

    def free_mem(self):
        """
        Free up memory.
        """
        self.size = 0
        self.briefList = []
        self.titleList = []
        self.namesList = []
        self.datesList = []
        gc.collect()

    def get_brief(self, query, content, n):
        """
        Obtain the brief description that shows up in search
        """
        query = query.lower()
        query = query.replace('\"', "")
        queryList = query.split()
        queryList.sort(key=len)
        content = content.lower().split()
        try:
            pos = content.index(query)
        except ValueError:
            pos = 0
        if (pos - n) < 0:
            start = 0
            end = pos + n + abs((pos - n))
        else:
            start = pos - n
            end = pos + n
        content = content[start:end]
        if len(content) >= 500:
            content = content[0:400]
        for query in queryList:
            wrap = '<font color=\'yellow\'><b>'+query+'</b></font>'
            try:
                content[content.index(query)] = wrap
            except ValueError:
                pass
        brief = " ".join(content)
        return brief

    def runSetup(self, jsonPath):
        self.pandas_to_json(jsonPath)
        self.save_json(self.searchIndex)

    def delete_duplicates(self , i):
        pass

    def delete_all(self, index='dark'):
        """
        Runs $ curl -XDELETE 'http://localhost:9200/your_index/'
        """
        r = requests.delete('http://localhost:9200/%s' % (index))
        print('Index %s deleted.' % index)

if __name__ == '__main__':
    test = DarkElastic()
    test.runSetup("../logs/process2.json")
    test.ingest_items()
    es.indices.refresh(index='dark')
    print(test.search_index('dark', 'cocaine', 15, 10))