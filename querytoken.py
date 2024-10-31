"""
 * Copyright (c) 2024-Present, Neo4j. and/or its affiliates. All rights reserved.
 *
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *
 * See the License for the specific language governing permissions and limitations under the License.
"""

# -*- coding: utf-8 -*-
# Generic/Built-in
import json
from typing import Dict
import os


# Other Libs
from requests import Request, Session
from requests.auth import HTTPBasicAuth, AuthBase
from neo4j import GraphDatabase, bearer_auth
from dotenv import load_dotenv

# Owned





class MyConfiguration():
    """
    Reads configuration from .env file in the same folder as this Python file
    """
    load_dotenv()
    OKTA_CLIENT_ID = os.getenv('OKTA_CLIENT_ID')
    OKTA_CLIENT_SECRET = os.getenv('OKTA_CLIENT_SECRET')
    OKTA_TOKEN_URI = os.getenv('OKTA_TOKEN_URI')
    OKTA_SCOPE = os.getenv('OKTA_SCOPE')
    NEO4J_URI = os.getenv('NEO4J_URI')

def make_request(request_url: str, request_operation: str, request_headers: dict, request_body,
                 request_auth: AuthBase) -> Dict:
    """
   Makes a request to Aura API and returns the JSON from the response
   :param request_url The path to the endpoint to make a request to
   :param request_operation The HTTP operation to perform for the request
   :param request_headers  A dictionary containing headers for the request
   :param request_body  The body of the request
   :param request_auth  Auth to use with the request
   :return: The JSON response back as a Python Dict
   """

    # A session will be used to avoid having to make a new connection with each request
    request_session = Session()

    # Prepare our request
    prepared_request = Request(request_operation, request_url, headers=request_headers, auth=request_auth,
                               data=request_body).prepare()

    try:
        # Send the request
        response = request_session.send(prepared_request)

    except Exception as e:
        print("%s raised an error: \n%s", aura_api_request, e)
        raise

    else:
        print(f"Reponse status code: {response.status_code} {response.reason}")
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            return {}


def get_token_from_okta(url: str, client_id: str, client_secret: str, token_scope: str):
    """
   Gets a token from Okta
   :param url: URL for Okta token
   :param client_id: Okta client id
   :param client_secret: Okta client secret
   :param token_scope: Okta scope

   """
    # Ask for a bearer token using the client id and client secret from Okta

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    body = {"grant_type": "client_credentials", "scope": token_scope}

    okta_response = make_request(url, 'POST', headers, body, HTTPBasicAuth(client_id, client_secret))

    if 'access_token' in okta_response:
        return okta_response['access_token']
    else:
        return None


def showcase_token_with_python_driver(config):
    okta_token = get_token_from_okta(config.OKTA_TOKEN_URI, config.OKTA_CLIENT_ID, config.OKTA_CLIENT_SECRET, config.OKTA_SCOPE)

    print(f"Okta token: {okta_token}")

    driver = GraphDatabase.driver(config.NEO4J_URI, auth=bearer_auth(okta_token))

    records, summary, keys = driver.execute_query(
        "MATCH (p:Person) RETURN p.name AS name",
        database_="neo4j",
    )

    # Loop through results and do something with them
    for record in records:
        print(record.data())  # obtain record as dict

    # Summary information
    print("The query `{query}` returned {records_count} records in {time} ms.".format(
        query=summary.query, records_count=len(records),
        time=summary.result_available_after
    ))

if __name__ == '__main__':
    showcase_token_with_python_driver(MyConfiguration)
