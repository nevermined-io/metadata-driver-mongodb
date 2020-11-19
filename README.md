[![banner](https://raw.githubusercontent.com/nevermined-io/assets/main/images/logo/banner_logo.png)](https://nevermined.io)

# metadata-driver-mongodb

>    🐳  [Mongo DB](https://www.mongodb.com/) driver for MetadataDB (Python).
> [nevermined.io](https://nevermined.io)
>
>[![PyPI](https://img.shields.io/pypi/v/nevermined-metadata-driver-mongodb.svg)](https://pypi.org/project/nevermined-metadata-driver-mongodb/)
[![Python package](https://github.com/nevermined-io/metadata-driver-mongodb/workflows/Python%20package/badge.svg)](https://github.com/nevermined-io/mmetadata-driver-mongodb/actions)

---

## Table of Contents

  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Quickstart](#quickstart)
  - [Environment variables](#environment-variables)
  - [Code style](#code-style)
  - [Testing](#testing)
  - [New Version](#new-version)
  - [License](#license)

---

## Features

MongoDB driver to connect implementing MetatadaDB.

## Prerequisites

You should have running a mongo instance.

## Quickstart

First of all we have to specify where is allocated our config.
To do that we have to pass the following argument:

```
--config=/path/of/my/config
```

If you do not provide a configuration path, by default the config is expected in the config folder.

In the configuration we are going to specify the following parameters to

```yaml

    [metadatadb]

    module=mongodb          # You can use one the plugins already created. Currently we have mongodb and bigchaindb.
    module.path=            # You can specify the location of your custom plugin.
    db.hostname=localhost   # Address of your MongoDB.
    db.port=27017           # Port of your Mongodb.

    db.ssl=True             # If True, connections will be made using HTTPS, else using HTTP
    db.verify_certs=False   # If True, CA certificate will be verified
    db.ca_cert_path=        # If verifyCerts is True, then path to the CA cert should be provided here
    db.client_key=          # If db server needs client verification, then provide path to your client key
    db.client_cert_path=    # If db server needs client verification, then provide path to your client certificate

    db.username=user        # If you are using authentication, mongodb username.
    db.password=password    # If you are using authentication, mongodb password.
    db.name=test            # Mongodb database name
    db.collection=col       # Mongodb collection name

```

Once you have defined this the only thing that you have to do it is use it:

```python

    metadatadb = MetadataDb(conf)
    metadatadb.write({"value": "test"}, id)

```

## Environment variables

When you want to instantiate an Metadatadb plugin you can provide the next environment variables:

- **$CONFIG_PATH**
- **$MODULE**
- **$DB_HOSTNAME**
- **$DB_PORT**
- **$DB_NAME**
- **$DB_COLLECTION**
- **$DB_USERNAME**
- **$DB_PASSWORD**


## Queries

Currently we are supporting a list of queries predefined in order to improve the search:
All this queries present a common format:
```query:{"name":[args]}```

This queries are the following:
- price

    Could receive one or two parameters. If you only pass one assumes that your query is going to start from 0 to your value.

    Next query:
    `query:{"price":[0,10]}`

    It is transformed to:
    `{"service.metadata.base.price":{"$gt": 0, "$lt": 10}}`

- license

    It is going to retrieve all the documents with license that you are passing in the parameters,
    if you do not pass any value retrieve all.

    `{"license":["Public domain", "CC-YB"]}`

- type

    It is going to check that the following service types are included in the ddo.

    `{"type":["Access", "Metadata"]}`

- sample

    Check that the metadata include a sample that contains a link of type sample. Do not take parameters.

    `{"sample":[]}`

- categories

    Retrieve all the values that contain one of the specifies categories.

    `{"categories":["weather", "meteorology"]}`

- created

    Retrieve all the values that has been created after a specified date.
    The parameters available are 'today', 'lastWeek', 'lastMonth', 'lastYear'. If you pass more than one take the bigger interval.
    If you do not pass any parameter retrieve everything.

    `{"created":["today"]}`

- updatedFrequency

    Retrieve all the values that contain one of the specifies updated frecuencies.

    `{"updatedFrequency":["monthly"]}`

- text

    Retrieve all the values that match with the text sent.

    `{"text":["weather"]}`


## Testing

Automatic tests are setup via Github actions.
Our test use pytest framework.

## New Version

The `bumpversion.sh` script helps to bump the project version. You can execute the script using as first argument {major|minor|patch} to bump accordingly the version.

## License

```
Copyright 2020 Keyko GmbH
This product includes software developed at
BigchainDB GmbH and Ocean Protocol (https://www.oceanprotocol.com/)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
