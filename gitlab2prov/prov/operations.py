import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional, Sequence
from urllib.parse import urlencode

from prov.identifier import QualifiedName
from prov.model import (
    ProvDocument,
    ProvRecord,
    ProvElement,
    ProvRelation,
    ProvAgent,
    ProvEntity,
    ProvActivity,
    PROV_ROLE,
    PROV_TYPE,
    PROV_REC_CLS,
)


log = logging.getLogger(__name__)


def qualified_name(localpart: str) -> QualifiedName:
    namespace = graph_factory().get_default_namespace()
    return QualifiedName(namespace, localpart)


def graph_factory(records: Optional[Sequence[ProvRecord]] = None) -> ProvDocument:
    if records is None:
        records = []
    graph = ProvDocument(records)
    graph.set_default_namespace("http://github.com/dlr-sc/gitlab2prov/")
    return graph


def combine(graphs: list[ProvDocument]) -> ProvDocument:
    log.info(f"combine graphs {graphs}")
    if not graphs:
        return graph_factory()
    acc = graphs[0]
    for graph in graphs[1:]:
        acc.update(graph)
    return acc


def dedupe(graph: ProvDocument) -> ProvDocument:
    log.info(f"deduplicate ProvElement's and ProvRelation's in {graph=}")
    graph = graph.unified()
    records = list(graph.get_records((ProvElement)))
    attrs = defaultdict(set)
    bundles = dict()

    for relation in graph.get_records(ProvRelation):
        rel = (type(relation), tuple(relation.formal_attributes))
        bundles[rel] = relation.bundle
        attrs[rel].update(relation.extra_attributes)

    for rel in attrs:
        bundle = bundles[rel]
        rtype, formal_attributes = rel
        attributes = list(formal_attributes)
        attributes.extend(attrs[rel])
        records.append(rtype(bundle, None, attributes))
    return graph_factory(records)


def read(fp: Path) -> dict[str, list[str]]:
    with open(fp, "r") as f:
        data = f.read()
        d = json.loads(data)
    if not d:
        log.info(f"empty agent mapping")
        return dict()
    return d


def xform(d: dict[str, list[str]]) -> dict[str, str]:
    return {alias: name for name, aliases in d.items() for alias in aliases}


def uncover_name(agent: str, names: dict[str, str]) -> tuple[QualifiedName, str]:
    [(qn, name)] = [
        (key, val) for key, val in agent.attributes if key.localpart == "name"
    ]
    return qn, names.get(name, name)


def uncover_double_agents(graph: ProvDocument, fp: str) -> ProvDocument:
    log.info(f"resolve aliases in {graph=}")
    # read mapping & transform
    names = xform(read(fp))
    # dict to temporarily store agent attributes
    attrs = defaultdict(set)
    # map of old agent identifiers to new agent identifiers
    # used to reroute relationships
    reroute = dict()
    # prov records that are not affected by this operation
    records = list(graph.get_records((ProvEntity, ProvActivity)))

    for agent in graph.get_records(ProvAgent):
        # resolve the agent alias (uncover its identity)
        name = uncover_name(agent, names)
        # rebuild the attributes of the current agent
        # start by adding the uncovered given name
        attrs[name].add(name)
        # add all other attributes aswell
        attrs[name].update(t for t in agent.attributes if t[0].localpart != "name")

        repr_attrs = [tpl for tpl in attrs[name] if tpl[1] in ("name", "email")]
        identifier = qualified_name(f"User?{urlencode(repr_attrs)}")
        records.append(ProvAgent(agent.bundle, identifier, attrs[name]))

        reroute[agent.identifier] = identifier

    for relation in graph.get_records(ProvRelation):
        attrs = [(k, reroute.get(v, v)) for k, v in relation.formal_attributes]
        # attrs.extend((k, reroute.get(v, v)) for k, v in relation.attributes)
        attrs.extend((k, reroute.get(v, v)) for k, v in relation.extra_attributes)
        r_type = PROV_REC_CLS.get(relation.get_type())
        records.append(r_type(relation.bundle, relation.identifier, attrs))

    return graph_factory(records).unified()


def pseudonymize(graph: ProvDocument):
    log.info(f"pseudonymize agents in {graph=}")
    keep = [PROV_ROLE, PROV_TYPE]

    agents = set(graph.get_records(ProvAgent))
    records = list(graph.get_records((ProvActivity, ProvEntity, ProvRelation)))

    for i, agent in enumerate(agents, start=1):
        # keep role, keep type, "forget" email, substitute name
        attributes = [(key, val) for key, val in agent.extra_attributes if key in keep]
        [(qn, _)] = [
            (key, val) for key, val in agent.extra_attributes if key.localpart == "name"
        ]
        attributes.append((qn, f"agent-{i}"))
        identifier = qualified_name(f"User?name=agent-{i}")
        records.append(ProvAgent(agent.bundle, identifier, attributes))

    return graph_factory(records)