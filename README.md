# GitLab2PROV - Extract Provenance Information from GitLab Repositories

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![DOI](https://zenodo.org/badge/215042878.svg)](https://zenodo.org/badge/latestdoi/215042878) ![Python application](https://github.com/DLR-SC/gitlab2prov/workflows/Python%20application/badge.svg?branch=master) ![mypy-check](https://github.com/DLR-SC/gitlab2prov/workflows/mypy-check/badge.svg) ![Deploy to Amazon ECS](https://github.com/DLR-SC/gitlab2prov/workflows/Deploy%20to%20Amazon%20ECS/badge.svg)

## Data Model

GitLab2PROV uses a data model according to [W3C PROV](https://www.w3.org/TR/prov-overview/) specification.

## Setup and Usage:rocket:

### Installation
```
# Clone repository via SSH (recommended)
git clone git@github.com:DLR-SC/gitlab2prov.git

# Change into directory
cd gitlab2prov

# Create a virtual environment (recommended)
python -m venv env

# Activate the environment
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

#### Obtain Private Access Token for GitLab

Go to https://YOUR-GITLAB/profile/personal_access_tokens and claim a personal access token.
The necessary scopes are `api` and `read_user`.

#### Configure Project

`gitlab2prov` is configured by its config file at `config/config.ini`.

Excerpt from `config/config.ini.example`

```ini
[GITLAB]
token = GitLabAPIToken
project = ProjectUrl
rate = RateLimit

[NEO4J]
host = Neo4jHost
user = Username
password = Password
boltport = BOLTPort
```

### Usage
```
usage: gitlab2prov.py [-h] [--provn PROVN] [--neo4j]

Extract provenance information from a GitLab repository.

optional arguments:
  -h, --help     show this help message and exit
  --provn PROVN  output file
  --neo4j        save to neo4j
```

## Example

### Cypher Query

```cypher
MATCH (user:Agent)-[:wasAttributedTo]-(fileVersion:Entity), (fileVersion:Entity)-[:specializationOf]->(file:Entity)
WHERE 
  fileVersion.`prov:type` = "file_version" AND file.`prov:type` = "file"
RETURN 
  user.name, COUNT(DISTINCT file) AS file_count
ORDER BY file_count DESC
```

## Credits
**Software that has provided the foundations for GitLab2PROV**  
* Martin Stoffers: "Gitlab2Graph", v1.0.0, October 13. 2019, [GitHub Link](https://github.com/DLR-SC/Gitlab2Graph), DOI 10.5281/zenodo.3469385  

* Quentin Pradet: "How do you rate limit calls with aiohttp?", [GitHub Gist](https://gist.github.com/pquentin/5d8f5408cdad73e589d85ba509091741), MIT LICENSE


**Papers that GitLab2PROV is based on**:

* De Nies, T., Magliacane, S., Verborgh, R., Coppens, S., Groth, P., Mannens, E., & Van de Walle, R. (2013). [Git2PROV: Exposing Version Control System Content as W3C PROV](https://dl.acm.org/doi/abs/10.5555/2874399.2874431). In *Poster and Demo Proceedings of the 12th International Semantic Web Conference* (Vol. 1035, pp. 125–128).

* Packer, H. S., Chapman, A., & Carr, L. (2019). [GitHub2PROV: provenance for supporting software project management](https://dl.acm.org/doi/10.5555/3359032.3359039). In *11th International Workshop on Theory and Practice of Provenance (TaPP 2019)*.
