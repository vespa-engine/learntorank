# AUTOGENERATED! DO NOT EDIT! File to edit: ../003_module_query.ipynb.

# %% auto 0
__all__ = ['MatchFilter', 'AND', 'OR', 'WeakAnd', 'Tokenize', 'ANN', 'Union', 'Ranking', 'QueryProperty', 'QueryRankingFeature',
           'QueryModel', 'send_query', 'send_query_batch', 'collect_vespa_features', 'store_vespa_features']

# %% ../003_module_query.ipynb 4
import os
from typing import Optional, Dict, Callable, List, Tuple, Union
from pandas import DataFrame
from fastcore.utils import patch
from vespa.io import VespaQueryResponse
from vespa.application import Vespa

# %% ../003_module_query.ipynb 6
class MatchFilter(object):
    def __init__(self) -> None:    
        "Abstract class for match filters."
        pass

# %% ../003_module_query.ipynb 7
@patch
def create_match_filter(
    self: MatchFilter, 
    query: str  # Query input.
) -> str:  # Part of the YQL expression related to the filter.
    "Abstract method to be implemented that creates part of the YQL expression related to the filter."
    raise NotImplementedError

# %% ../003_module_query.ipynb 8
@patch
def get_query_properties(
    self: MatchFilter, 
    query: Optional[str] = None  # Query input.
) -> Dict:  # Contains the relevant request properties associated with the filter.
    "Abstract method to be implemented that get the relevant request properties associated with the filter."
    raise NotImplementedError

# %% ../003_module_query.ipynb 9
class AND(MatchFilter):
    def __init__(self) -> None:
        "Filter that match document containing all the query terms."
        super().__init__()

# %% ../003_module_query.ipynb 12
@patch
def create_match_filter(
    self: AND, 
    query: str  # Query input.  
) -> str:  # Part of the YQL expression related to the AND filter.
    "Creates part of the YQL expression related to the AND filter"
    return '(userInput("{}"))'.format(query)

# %% ../003_module_query.ipynb 13
@patch
def get_query_properties(
    self: AND, 
    query: Optional[str] = None  # Query input.
) -> Dict:  # Get the relevant request properties associated with the AND filter.
    "Get the relevant request properties associated with the AND filter."
    return {}


# %% ../003_module_query.ipynb 15
class OR(MatchFilter):
    def __init__(self) -> None:
        "Filter that match any document containing at least one query term."
        super().__init__()

# %% ../003_module_query.ipynb 18
@patch
def create_match_filter(
    self: OR, 
    query: str  # Query input.
) -> str:  # Part of the YQL expression related to the OR filter.
    "Creates part of the YQL expression related to the OR filter"    
    return '({{grammar: "any"}}userInput("{}"))'.format(query)

# %% ../003_module_query.ipynb 19
@patch
def get_query_properties(
    self: OR, 
    query: Optional[str] = None  # Query input.
) -> Dict:  # Get the relevant request properties associated with the OR filter.
    "Get the relevant request properties associated with the OR filter."    
    return {}

# %% ../003_module_query.ipynb 21
class WeakAnd(MatchFilter):
    def __init__(
        self, 
        hits: int,  # Lower bound on the number of hits to be retrieved. 
        field: str = "default"  # Which Vespa field to search.
    ) -> None:
        """
        Match documents according to the weakAND algorithm.

        Reference: [https://docs.vespa.ai/en/using-wand-with-vespa.html](https://docs.vespa.ai/en/using-wand-with-vespa.html)
        """
        super().__init__()
        self.hits = hits
        self.field = field

# %% ../003_module_query.ipynb 24
@patch
def create_match_filter(
    self: WeakAnd, 
    query: str  # Query input.
) -> str:  # Part of the YQL expression related to the WeakAnd filter.
    "Creates part of the YQL expression related to the WeakAnd filter"
    return '({{grammar: "weakAnd", targetHits: {}, defaultIndex: "{}"}}userInput("{}"))'.format(self.hits, self.field, query)


# %% ../003_module_query.ipynb 25
@patch
def get_query_properties(
    self: WeakAnd, 
    query: Optional[str] = None  # Query input.
) -> Dict:  # Get the relevant request properties associated with the WeakAnd filter.
    "Get the relevant request properties associated with the WeakAnd filter."        
    return {}

# %% ../003_module_query.ipynb 27
class Tokenize(MatchFilter):
    def __init__(
        self, 
        hits: int,  # Lower bound on the number of hits to be retrieved. 
        field: str = "default"  # Which Vespa field to search.
    ) -> None:
        """
        Match documents according to the weakAND algorithm without parsing specials characters.

        Reference: [https://docs.vespa.ai/en/reference/simple-query-language-reference.html](https://docs.vespa.ai/en/reference/simple-query-language-reference.html)
        """
        super().__init__()
        self.hits = hits
        self.field = field

# %% ../003_module_query.ipynb 30
@patch
def create_match_filter(
    self: Tokenize, 
    query: str  # Query input.
) -> str:  # Part of the YQL expression related to the Tokenizer filter.
    "Creates part of the YQL expression related to the Tokenizer filter"
    return '({{grammar: "tokenize", targetHits: {}, defaultIndex: "{}"}}userInput("{}"))'.format(self.hits, self.field, query)

# %% ../003_module_query.ipynb 31
@patch
def get_query_properties(
    self: Tokenize, 
    query: Optional[str] = None  # Query input.
) -> Dict:  # Get the relevant request properties associated with the Tokenize filter.
    "Get the relevant request properties associated with the Tokenize filter."        
    return {}

# %% ../003_module_query.ipynb 33
class ANN(MatchFilter):
    def __init__(
        self,
        doc_vector: str,  # Name of the document field to be used in the distance calculation.
        query_vector: str,  # Name of the query field to be used in the distance calculation.
        hits: int,  # Lower bound on the number of hits to return.
        label: str,  # A label to identify this specific operator instance.
        approximate: bool = True,  # True to use approximate nearest neighbor and False to use brute force. Default to True.
    ) -> None:
        """
        Match documents according to the nearest neighbor operator.

        Reference: [https://docs.vespa.ai/en/reference/query-language-reference.html](https://docs.vespa.ai/en/reference/query-language-reference.html)
        """
        super().__init__()
        self.doc_vector = doc_vector
        self.query_vector = query_vector
        self.hits = hits
        self.label = label
        self.approximate = approximate
        self._approximate = "true" if self.approximate is True else "false"

# %% ../003_module_query.ipynb 39
@patch
def create_match_filter(
    self: ANN, 
    query: str  # Query input is ignored in the ANN case.
) -> str:  # Part of the YQL expression related to the ANN filter.
    "Creates part of the YQL expression related to the ANN filter"    
    return '({{targetHits: {}, label: "{}", approximate: {}}}nearestNeighbor({}, {}))'.format(
        self.hits, self.label, self._approximate, self.doc_vector, self.query_vector
    )

# %% ../003_module_query.ipynb 40
@patch
def get_query_properties(
    self: ANN, 
    query: Optional[str] = None  # Query input is ignored in the ANN case.
) -> Dict[str, str]:  # Get the relevant request properties associated with the ANN filter.
    "Get the relevant request properties associated with the ANN filter."            
    return {}

# %% ../003_module_query.ipynb 43
class Union(MatchFilter):
    def __init__(
        self, 
        *args: MatchFilter  # Match filters to be taken the union of.
    ) -> None:
        "Match documents that belongs to the union of many match filters."
        super().__init__()
        self.operators = args

# %% ../003_module_query.ipynb 46
@patch
def create_match_filter(
    self: Union, 
    query: str  # Query input.
) -> str:  # Part of the YQL expression related to the Union filter.
    "Creates part of the YQL expression related to the Union filter"    
    match_filters = []
    for operator in self.operators:
        match_filter = operator.create_match_filter(query=query)
        if match_filter is not None:
            match_filters.append(match_filter)
    return " or ".join(match_filters)

# %% ../003_module_query.ipynb 47
@patch
def get_query_properties(
    self: Union,  # Query input. 
    query: Optional[str] = None  # Get the relevant request properties associated with the Union filter.
) -> Dict[str, str]:  # Get the relevant request properties associated with the Union filter.
    query_properties = {}
    for operator in self.operators:
        query_properties.update(operator.get_query_properties(query=query))
    return query_properties

# %% ../003_module_query.ipynb 50
class Ranking(object):
    def __init__(
        self, 
        name: str = "default",  # Name of the rank profile as defined in a Vespa search definition.
        list_features: bool = False  # Should the ranking features be returned. Either 'true' or 'false'.
    ) -> None:
        "Define the rank profile to be used during ranking."
        self.name = name
        self.list_features = "false"
        if list_features:
            self.list_features = "true"

# %% ../003_module_query.ipynb 55
class QueryProperty(object):
    def __init__(self) -> None:    
        "Abstract class for query property."
        pass    

# %% ../003_module_query.ipynb 56
@patch
def get_query_properties(
    self: QueryProperty, 
    query: Optional[str] = None  # Query input.
) -> Dict:  # Contains the relevant request properties to be included in the query.
    "Extract query property syntax."
    raise NotImplementedError


# %% ../003_module_query.ipynb 57
class QueryRankingFeature(QueryProperty):
    def __init__(
        self,
        name: str,  # Name of the feature.
        mapping: Callable[[str], List[float]],  # Function mapping a string to a list of floats.
    ) -> None:
        "Include ranking.feature.query into a Vespa query."
        super().__init__()
        self.name = name
        self.mapping = mapping

# %% ../003_module_query.ipynb 60
@patch
def get_query_properties(
    self: QueryRankingFeature, 
    query: Optional[str] = None  # Query input.
) -> Dict[str, str]:  # Contains the relevant request properties to be included in the query.
    value = self.mapping(query)
    return {"ranking.features.query({})".format(self.name): str(value)}

# %% ../003_module_query.ipynb 63
class QueryModel(object):
    def __init__(
        self,
        name: str = "default_name",  # Name of the query model. Used to tag model-related quantities, like evaluation metrics.
        query_properties: Optional[List[QueryProperty]] = None,  # Query properties to be included in the queries.
        match_phase: MatchFilter = AND(),  # Define the match criteria.
        ranking: Ranking = Ranking(),  # Define the rank criteria.
        body_function: Optional[Callable[[str], Dict]] = None,  # Function that take query as parameter and returns the body of a Vespa query.
    ) -> None:
        """
        Define a query model.

        A `QueryModel` is an abstraction that encapsulates all the relevant information
        controlling how a Vespa app matches and ranks documents.
        """
        self.name = name
        self.query_properties = query_properties if query_properties is not None else []
        self.match_phase = match_phase
        self.ranking = ranking
        self.body_function = body_function


# %% ../003_module_query.ipynb 71
@patch
def create_body(
    self: QueryModel, 
    query: str  # Query string.
) -> Dict[str, str]:  # Request body
    "Create the appropriate request body to be sent to Vespa."

    if self.body_function:
        body = self.body_function(query)
        return body

    query_properties = {}
    for query_property in self.query_properties:
        query_properties.update(query_property.get_query_properties(query=query))
    query_properties.update(self.match_phase.get_query_properties(query=query))

    match_filter = self.match_phase.create_match_filter(query=query)

    body = {
        "yql": "select * from sources * where {};".format(match_filter),
        "ranking": {
            "profile": self.ranking.name,
            "listFeatures": self.ranking.list_features,
        },
    }
    body.update(query_properties)
    return body

# %% ../003_module_query.ipynb 78
def _build_query_body(
    query: str,
    query_model: QueryModel,
    recall: Optional[Tuple] = None,
    **kwargs,
) -> Dict:
    assert query_model is not None, "No 'query_model' specified."
    body = query_model.create_body(query=query)
    if recall is not None:
        body.update(
            {
                "recall": "+("
                + " ".join(
                    ["{}:{}".format(recall[0], str(doc)) for doc in recall[1]]
                )
                + ")"
            }
        )
    body.update(kwargs)
    return body

# %% ../003_module_query.ipynb 79
def send_query(
    app: Vespa,  # Connection to a Vespa application
    body: Optional[Dict] = None,  # Contains all the request parameters. None when using `query_model`.
    query: Optional[str] = None,  # Query string. None when using `body`.
    query_model: Optional[QueryModel] = None,  # Query model. None when using `body`.
    debug_request: bool = False,  # Return request body for debugging instead of sending the request.
    recall: Optional[Tuple] = None,  # Tuple of size 2 where the first element is the name of the field to use to recall and the second element is a list of the values to be recalled.
    **kwargs,  # Additional parameters to be sent along the request.
) -> VespaQueryResponse:  # Either the request body if debug_request is True or the result from the Vespa application.
    """
    Send a query request to a Vespa application.

    Either send 'body' containing all the request parameters or specify 'query' and 'query_model'.
    """
    body = (
        _build_query_body(query, query_model, recall, **kwargs)
        if body is None
        else body
    )
    if debug_request:
        return VespaQueryResponse(
            json={}, status_code=None, url=None, request_body=body
        )
    else:
        return app.query(body=body)

# %% ../003_module_query.ipynb 98
def send_query_batch(
    app,  # Connection to a Vespa application
    body_batch: Optional[List[Dict]] = None,  # Contains all the request parameters. Set to None if using 'query_batch'.
    query_batch: Optional[List[str]] = None,  # Query strings. Set to None if using 'body_batch'.
    query_model: Optional[QueryModel] = None,  # Query model to use when sending query strings. Set to None if using 'body_batch'.
    recall_batch: Optional[List[Tuple]] = None,  # One tuple for each query. Tuple of size 2 where the first element is the name of the field to use to recall and the second element is a list of the values to be recalled.
    asynchronous=True,  # Set True to send data in async mode. Default to True.
    connections: Optional[int] = 100,  # Number of allowed concurrent connections, valid only if `asynchronous=True`.
    total_timeout: int = 100,  # Total timeout in secs for each of the concurrent requests when using `asynchronous=True`.
    **kwargs,  # Additional parameters to be sent along the request.
) -> List[VespaQueryResponse]:  # HTTP POST responses.
    "Send queries in batch to a Vespa app."

    if body_batch:
        assert (
            query_batch is None
        ), "'query_batch' has no effect if 'body_batch' is not None."
    elif query_batch:
        assert (
            body_batch is None
        ), "'body_batch' has no effect if 'query_batch' is not None."
        assert (
            query_model is not None
        ), "Specify a 'query_model' when using 'query_batch' argument."
        number_of_queries = len(query_batch)

        if recall_batch:
            assert (
                len(recall_batch) == number_of_queries
            ), "Specify one recall tuple for each query in the batch."
            body_batch = [
                _build_query_body(
                    query=query, 
                    query_model=query_model, 
                    recall=recall,
                    **kwargs
                ) for query, recall in zip(query_batch, recall_batch)
            ]
        else:
            body_batch = [
                _build_query_body(
                    query=query, 
                    query_model=query_model, 
                    **kwargs
                ) for query in query_batch
            ]
    else:
        ValueError("Specify either 'query_batch' or 'body_batch'.")

    return app.query_batch(
        body_batch=body_batch,
        asynchronous=asynchronous,
        connections=connections,
        total_timeout=total_timeout,
    )

# %% ../003_module_query.ipynb 109
def _annotate_data(
    hits, query_id, id_field, relevant_id, fields, relevant_score, default_score
):
    data = []
    for h in hits:
        record = {}
        record.update({"document_id": h["fields"][id_field]})
        record.update({"query_id": query_id})
        record.update(
            {
                "label": relevant_score
                if h["fields"][id_field] == relevant_id
                else default_score
            }
        )
        for field in fields:
            field_value = h["fields"].get(field, None)
            if field_value:
                if isinstance(field_value, dict):
                    record.update(field_value)
                else:
                    record.update({field: field_value})
        data.append(record)
    return data


# %% ../003_module_query.ipynb 110
def _parse_labeled_data(
    df: DataFrame  # DataFrame with the following required columns ["qid", "query", "doc_id", "relevance"].
) -> List[Dict]:  # Concise representation of the labeled data, grouped by query_id and query.
    "Convert a DataFrame with labeled data to format used internally"
    required_columns = ["qid", "query", "doc_id", "relevance"]
    assert all(
        [x in list(df.columns) for x in required_columns]
    ), "DataFrame needs at least the following columns: {}".format(required_columns)
    qid_query = (
        df[["qid", "query"]].drop_duplicates(["qid", "query"]).to_dict(orient="records")
    )
    labeled_data = []
    for q in qid_query:
        docid_relevance = df[(df["qid"] == q["qid"]) & (df["query"] == q["query"])][
            ["doc_id", "relevance"]
        ]
        relevant_docs = []
        for idx, row in docid_relevance.iterrows():
            relevant_docs.append({"id": row["doc_id"], "score": row["relevance"]})
        data_point = {
            "query_id": q["qid"],
            "query": q["query"],
            "relevant_docs": relevant_docs,
        }
        labeled_data.append(data_point)
    return labeled_data

# %% ../003_module_query.ipynb 114
def collect_vespa_features(
    app: Vespa,  # Connection to a Vespa application.
    labeled_data,  # Labelled data containing query, query_id and relevant ids. See examples about data format.
    id_field: str,  # The Vespa field representing the document id.
    query_model: QueryModel,  # Query model.
    number_additional_docs: int,  # Number of additional documents to retrieve for each relevant document. Duplicate documents will be dropped.
    fields: List[str],  # Vespa fields to collect, e.g. ["rankfeatures", "summaryfeatures"]
    keep_features: Optional[List[str]] = None,  # List containing the names of the features that should be returned. Default to None, which return all the features contained in the 'fields' argument.
    relevant_score: int = 1,  # Score to assign to relevant documents. Default to 1.
    default_score: int = 0,  # Score to assign to the additional documents that are not relevant. Default to 0.
    **kwargs,  # Extra keyword arguments to be included in the Vespa Query.
) -> DataFrame:  # DataFrame containing document id (document_id), query id (query_id), scores (relevant) and vespa rank features returned by the Query model RankProfile used.
    """
    Collect Vespa features based on a set of labelled data.
    """

    if isinstance(labeled_data, DataFrame):
        labeled_data = _parse_labeled_data(df=labeled_data)

    flat_data = [
        (
            data["query_id"],
            data["query"],
            relevant_doc["id"],
            relevant_doc.get("score", relevant_score),
        )
        for data in labeled_data
        for relevant_doc in data["relevant_docs"]
    ]

    queries = [x[1] for x in flat_data]
    relevant_search = send_query_batch(
        app=app,
        query_batch=queries,
        query_model=query_model,
        recall_batch=[(id_field, [x[2]]) for x in flat_data],
        **kwargs,
    )
    result = []
    for ((query_id, query, relevant_id, relevant_score), query_result) in zip(
        flat_data, relevant_search
    ):
        result.extend(
            _annotate_data(
                hits=query_result.hits,
                query_id=query_id,
                id_field=id_field,
                relevant_id=relevant_id,
                fields=fields,
                relevant_score=relevant_score,
                default_score=default_score,
            )
        )
    if number_additional_docs > 0:
        additional_hits_result = send_query_batch(
            app=app,
            query_batch=queries,
            query_model=query_model,
            hits=number_additional_docs,
            **kwargs,
        )
        for ((query_id, query, relevant_id, relevant_score), query_result) in zip(
            flat_data, additional_hits_result
        ):
            result.extend(
                _annotate_data(
                    hits=query_result.hits,
                    query_id=query_id,
                    id_field=id_field,
                    relevant_id=relevant_id,
                    fields=fields,
                    relevant_score=relevant_score,
                    default_score=default_score,
                )
            )
    df = DataFrame.from_records(result)
    df = df.drop_duplicates(["document_id", "query_id", "label"])
    df = df.sort_values("query_id")
    if keep_features:
        df = df[["document_id", "query_id", "label"] + keep_features]
    return df

# %% ../003_module_query.ipynb 129
def store_vespa_features(
    app: Vespa,  # Connection to a Vespa application.
    output_file_path: str,  # Path of the .csv output file. It will create the file of it does not exist and append the vespa features to an pre-existing file.
    labeled_data,  # Labelled data containing query, query_id and relevant ids. See details about data format.
    id_field: str,  # The Vespa field representing the document id.
    query_model: QueryModel,  # Query model.
    number_additional_docs: int,  # Number of additional documents to retrieve for each relevant document.
    fields: List[str],  # List of Vespa fields to collect, e.g. ["rankfeatures", "summaryfeatures"]
    keep_features: Optional[List[str]] = None,  # List containing the names of the features that should be returned. Default to None, which return all the features contained in the 'fields' argument.
    relevant_score: int = 1,  # Score to assign to relevant documents.
    default_score: int = 0,  # Score to assign to the additional documents that are not relevant.
    batch_size=1000,  # The size of the batch of labeled data points to be processed.
    **kwargs,  # Extra keyword arguments to be included in the Vespa Query.
) -> int:  # returns 0 upon success.
    "Retrieve Vespa rank features and store them in a .csv file."

    if isinstance(labeled_data, DataFrame):
        labeled_data = _parse_labeled_data(df=labeled_data)

    mini_batches = [
        labeled_data[i : i + batch_size]
        for i in range(0, len(labeled_data), batch_size)
    ]
    for idx, mini_batch in enumerate(mini_batches):
        vespa_features = collect_vespa_features(
            app=app,
            labeled_data=mini_batch,
            id_field=id_field,
            query_model=query_model,
            number_additional_docs=number_additional_docs,
            fields=fields,
            keep_features=keep_features,
            relevant_score=relevant_score,
            default_score=default_score,
            **kwargs,
        )
        if os.path.isfile(output_file_path):
            vespa_features.to_csv(
                path_or_buf=output_file_path, header=False, index=False, mode="a"
            )
        else:
            vespa_features.to_csv(
                path_or_buf=output_file_path, header=True, index=False, mode="w"
            )
        print(
            "Rows collected: {}.\nBatch progress: {}/{}.".format(
                vespa_features.shape[0],
                idx + 1,
                len(mini_batches),
            )
        )
    return 0

