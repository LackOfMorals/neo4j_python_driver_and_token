
---

# Applications, Tokens and Neo4j Python Driver

Using tokens for auth with Neo4j Python Driver 
================================================

We will need

* A free Okta developer account

* Neo4j Enterprise running in Docker locally

* Docker installed

* A local copy of curl

* Text editor

## Neo4j Docker image

### Install & Run the Neo4j Docker image

**Note**:  If you are not comfortable with the values used for the username & password , change NEO4J_AUTH=neo4j/password to  something that works for you.

The neo4j docker image will use folders in the home directory.  Create those first

```Bash
mkdir -p ~/neo4j/conf
mkdir -p ~/neo4j/data
mkdir -p ~/neo4j/logs
```
  
Tell Docker to download and run Neo4j

```Bash
docker run -dt \
--name=neo4jDb \
--publish=7474:7474 \
--publish=7687:7687 \
--volume=$HOME/neo4j/data:/data \
--volume=$HOME/neo4j/conf:/conf \
--volume=$HOME/neo4j/logs:/logs \
--env=NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
--env=NEO4J_AUTH=neo4j/password \
neo4j:enterprise
```

### Test

Check Neo4j is up and running by going to this local URL [http://localhost:7474/browser](http://localhost:7474/browser)

This should show you the Browser console for Neo4j.  Auth using neo4j for the user and password for the password.

* * *

Okta configuration
==================

This requires configuration work in two areas of the Okta console; Applications and  Security and also obtaining the developer account Okta Domain.  

Okta developer account domain
------------

Before starting any work , we need the developer account okta domain.  Locate this by going to the top right and selecting your account.  From the drop down menu , you will see your email address and immediately underneath the domain for your developer account.  Make a note of this.

Applications
------------

**Applications** -> **Create App Integration** -> **API Services**

* Provide a name e.g neo4j m2m query api for API Service

When the new API Service is shown :-

### General

Client credentials

* Client ID: Copy the client id as this will be needed later

* Client authentication: Client secret

CLIENT SECRETS

* Client secret:   Copy this as it also will be needed later

General Setting

* Proof of possession :  Make sure Require Demonstrating Proof of Possession (DPoP) header in token requests is not selected

Security
--------

**Security** -> **API** -> **Add Authorization Server**

* Name:  Give this a meaningful name e.g neo4j query api

* Audience: This will form part of the generated token.  Suggest using that is short and descriptive e.g neo4j-query-api.  This will be needed for Neo4j configuration

* Description: Enter some words that describe what this is for

The newly created authorization server is now displayed.

The next step is to create a Scope which will be used in the Neo4j configuration to map to a Neo4j role.  This determines the access level that will be granted.

Select **Scopes**

### Add Scope

* Name: Provide a name for the scope e.g Neo4jDba

* Display phrase:  Enter what this is for e.g DBA access

* Description: Longer description e.g DBA level access for Neo4j

* User consent:  Implicit

* Block services :  Not checked

* Default scope:  If checked, this will be given to any token request that does not explicitly ask for a scope.  Advise that this is not checked.

* Metadata:  The scope will be included in the response from the well known API and hence visible.  Advise that this is not checked.

Select **Create**

The newly created scope will now be shown in the table.  Make a note of the **Issuer URI**


### Access Policies
You will need to allow access by clients to new authorization server.   Missing this step will result in access denied messages when trying to obtain a token.  
Creating an **Access Policy**
Select **Access Policies** -> **Add New Access Policy**
**Name**: Enter a name
**Description**: Enter a description
**Assign To**:  All Clients

When access policy is created and shown, within the policy select **Add Rule**
Enter a name for the rule.  The default settings will be fine and do not need to be changed for our purposes but should be carefully considered for production use. 
Select **Create Rule** to create the rule



Takeways from Okta configuration work
--------

Once Okta is configured, we will have

* Developer account domain

* Client ID

* Client Secret

* Issuer URI

* Audience

* Scope

* * *

Neo4j configuration
-------------------

It's entirely possible for Neo4j to have more than one configured ODIC provider.  It's also possible to hide an entry from users of the Neo4j web Browser console, something that we will need to do as the configuration for an application to use token is not going to work for a user.

This is line that we'll need to use with our OIDC configuration entry
```dbms.ecurity.oidc.YOUR_OIDC_ENTYR_NAME.visible=false```

Edit neo4j.conf and add this in the OIDC section swapping out these values for yours from Okta.

* YOUR_AUDIENCE_ID_FROM_OKTA

* YOUR_CLIENT_ID_FROM_OKTA

* YOUR_CLIENT_SECRET_ID_FROM_OKTA

* YOUR_ISSUER_URI_FROM_OKTA

* YOUR_SCOPE_FROM_OKTA

```Text
# Okta m2m settings
dbms.ecurity.oidc.m2m.visible=false
dbms.security.oidc.m2m.display_name=m2m
dbms.security.oidc.m2m.auth_flow=pkce
dbms.security.oidc.m2m.well_known_discovery_uri=YOUR_ISSUER_URI_FROM_OKTA/.well-known/openid-configuration
dbms.security.oidc.m2m.audience=YOUR_AUDIENCE_ID_FROM_OKTA
dbms.security.oidc.m2m.client_id=YOUR_CLIENT_ID_FROM_OKTA
dbms.security.oidc.m2m.claims.groups=scp
dbms.security.oidc.m2m.claims.username=sub
dbms.security.oidc.m2m.params=client_id=YOUR_CLIENT_ID_FROM_OKTA;response_type=code;scope=openid profile scp
dbms.security.oidc.m2m.authorization.group_to_role_mapping=YOUR_SCOPE_FROM_OKTA=admin
```

Save the file and then restart Neo4j.

```Bash
docker restart neo4jDb
```

* * *

Getting a token from Okta
-----------------------------------------

A token to use with the Query API is obtained from **YOUR_ISSUER_URI_FROM_OKTA/v1/token**  as illustrated with this example using CURL

Replace

* YOUR_ISSUER_URI_FROM_OKTA

* YOUR_SCOPE_FROM_OKTA

* YOUR_CLIENT_ID_FROM_OKTA

* YOUR_CLIENT_SECRET_ID_FROM_OKTA

with values from the Okta configuration

```Bash
curl --request POST \

--url YOUR_ISSUER_URI_FROM_OKTA/v1/token \
--header 'accept: application/json' \
--header 'cache-control: no-cache' \
--header 'content-type: application/x-www-form-urlencoded' \
--data 'grant_type=client_credentials&scope=YOUR_SCOPE_FROM_OKTA' \
-u CLIENT_ID:CLIENT_SECRET
```

This should result in a response that looks similar to this

```JSON
{
"token_type": "Bearer",
"expires_in": 3600,
"access_token": "eyJraWQiOiJfM0lPdk9tUEJGN3hKN2FPbHNmYzVKWmlGWXdua1Q4WHY5ZG9hYk9JOEhFIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmZkYjJ3eGZPMFJaSmFiUDNIUkxGLVl6VFpHczhkTVFYUnJLWU02aUFlemsiLCJpc3MiOiJodHRwczovL2Rldi04NTI1NzgzOC5va3RhLmNvbS9vYXV0aDIvZGVmYXVsdCIsImF1ZCI6Im5lbzRqLWF1ZCIsImlhdCI6MTcyOTYzMzA2MiwiZXhwIjoxNzI5NjM2NjYyLCJjaWQiOiIwb2FrZ2R4eHJyM3FiVkhFRDVkNyIsInNjcCI6WyJuZW80akRiYSJdLCJzdWIiOiIwb2FrZ2R4eHJyM3FiVkhFRDVkNyJ9.CGHx-dnhKd1d_i_hEroNHOCPUYROh0wqz2EuKCDYuieiIkqx9sG1Z8f1hnb96FL2uyyTL2bpAILiG3-85urVeG-6R5Dazf87opM5IyLhYTxboM5VjF3xsKsUiSjIQBP7jsCqHFxCsBpOB2nUSxzmk3NZpVhV2oZJK5-WBl1wCj7ttyAeuZ7sbm44SdrdIz9pmf6RmTQ30nBexZ6ccNx7YxxZZyo2jJeRvNDOn-yRpydkOOOqe7kR1qk7qhG14cKLQBgmx2RL5DAxG9ZJOHh1dUcOE87duhT3uD476JmcmS8DG589CCO3bMcmORYLkArf_5QFWW-bG8FJy5UGJVffFA",
"scope": "neo4jDba"
}
```

* * *

## The Python application

Create a .env file with this content.  Replace with your values

This file needs to be in the same folder as the main Python filae, querytoken.py

```Text
OKTA_CLIENT_ID = "YOUR_CLIENT_ID_FROM_OKTA"
OKTA_CLIENT_SECRET = "YOUR_CLIENT_SECRET_ID_FROM_OKTA"
OKTA_TOKEN_URI = "YOUR_ISSUER_URI_FROM_OKTA/v1/token"
OKTA_SCOPE = "YOUR_SCOPE_FROM_OKTA"
NEO4J_URI = "YOUR_NEO4J_URI:7687"

```

Install  the requirements

```Bash
pip install -r requirements.txt
```


Run the Python app
```Bash
python querytoken.py
```

