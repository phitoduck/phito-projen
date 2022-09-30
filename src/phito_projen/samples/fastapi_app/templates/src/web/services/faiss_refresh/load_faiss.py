"""Logic for fetching a FAISS faiss_index and using it for inference."""

import pickle
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional, Union

import boto3
import faiss
from faiss.swigfaiss import IndexIVFFlat
from godrics_hollow import GodricsHollow

from ben_similarity.config import LOGGER
from ben_similarity.default_constants import DEFAULT__FAISS_INDEX_N_PROBE
from ben_similarity.types import ProductionHost


def fetch_current_model_id(gh_secret_id: str, gh: Optional[GodricsHollow] = None) -> IndexIVFFlat:
    """
    Fetch the ID of the FAISS faiss_index that should be used for inference.

    When a new FAISS faiss_index trained with the latest influencer data,
    the FAISS faiss_index file is saved and made accessible with an ID.

    The ID of the FAISS faiss_index that should be used for inference is stored
    in a central secrets manager.

    :param gh_secret_id: Godrics Hollow secret id containing the model id of the model to fetch
    :param gh: :class:`GodricsHollow` instance used to fetch the secret

    :returns: FAISS faiss_index ID
    """
    if not gh:
        gh = GodricsHollow()
    response: dict = gh.get_secret(gh_secret_id)
    return response["model-id"]


def load_faiss_index_from_model_registry(host: ProductionHost, bucket: str, model_id: str) -> IndexIVFFlat:
    """
    Fetch a fitted FAISS faiss_index from our model registry by ID.

    The FAISS faiss_index is a 2-d matrix where the columns represent productions
    (YouTube Channels, Instragram accounts, etc.).

    :param bucket: s3 bucket containing the FAISS faiss_index
    :param model_id: ID of the FAISS faiss_index artifact in S3

    :return: a FAISS faiss_index object which can be used for inference
    """
    with TemporaryDirectory() as temp_dir:
        download_to_fpath = str(Path(temp_dir) / "model.faiss")
        download_faiss_index(host=host, bucket=bucket, model_id=model_id, out_fpath=download_to_fpath)
        faiss_index = faiss.read_index(download_to_fpath)
        faiss_index.nprobe = DEFAULT__FAISS_INDEX_N_PROBE
        return faiss_index


def load_faiss_production_ids_from_model_registry(
    host: ProductionHost, bucket: str, model_id: str
) -> List[str]:
    """
    Fetch a list of production IDs to be used with a FAISS faiss_index of the same ``model_id``.

    .. note:: The i'th ID corresponds to the i'th column of the FAISS faiss_index.

    :param bucket: s3 bucket containing the FAISS faiss_index
    :param model_id: ID of the FAISS faiss_index artifact in S3

    :return: list of production ids where the faiss_index of the production
    """
    with TemporaryDirectory() as temp_dir:
        download_to_fpath = str(Path(temp_dir) / "production-ids-in-faiss.pickle")
        download_faiss_production_ids(host=host, bucket=bucket, model_id=model_id, out_fpath=download_to_fpath)
        with open(download_to_fpath, "rb") as productions_pkl_file:
            faiss_index_production_ids: List[str] = pickle.load(productions_pkl_file)
            return faiss_index_production_ids


def download_s3_file(bucket: str, s3_key: str, out_fpath: Union[Path, str]):
    """
    Stream a file into memory as bytes.

    :param bucket: name of the s3 bucket containing the file
    :param s3_key: path to the object in s3 without the bucket name
    :param out_fpath: where to write the S3 file on disk
    """
    log_data = {
        "bucket": bucket,
        "key": s3_key,
    }
    LOGGER.bind(**log_data).info("Fetching file from S3.")
    s3_client = boto3.client("s3")
    s3_client.download_file(Bucket=bucket, Key=s3_key, Filename=str(out_fpath))


def download_faiss_index(host: ProductionHost, bucket: str, model_id: str, out_fpath: Union[Path, str]):
    """
    Download a FAISS file to the specified ``out_fpath`` on disk.

    :param bucket: s3 bucket containing the FAISS faiss_index
    :param model_id: ID of the FAISS faiss_index artifact in S3
    :out_fpath: location to save the FAISS faiss_index artifact on disk
    """
    faiss_index_s3_key: str = make_faiss_index_s3_key(host=host, model_id=model_id)
    download_s3_file(bucket=bucket, s3_key=faiss_index_s3_key, out_fpath=out_fpath)


def download_faiss_production_ids(
    host: ProductionHost, bucket: str, model_id: str, out_fpath: Union[Path, str]
):
    """
    Download a FAISS file to the specified ``out_fpath`` on disk.

    :param bucket: s3 bucket containing the FAISS faiss_index
    :param model_id: ID of the FAISS faiss_index artifact in S3
    :out_fpath: location to save the FAISS faiss_index artifact on disk
    """
    production_ids_pickle_s3_key: str = make_production_id_faiss_indices_s3_key(host=host, model_id=model_id)
    download_s3_file(bucket=bucket, s3_key=production_ids_pickle_s3_key, out_fpath=out_fpath)


def make_production_id_faiss_indices_s3_key(host: ProductionHost, model_id: str) -> str:
    """
    See return section.

    :param model_id: model id of the desired production IDs artifact in S3
    :return: s3 key of the production IDs used in a FAISS faiss_index
    """
    _host: str = host.value
    return f"{_host}-graphs/index-production-ids/{_host}_graph_production_ids_{model_id}.pickle"


def make_faiss_index_s3_key(host: ProductionHost, model_id: str) -> str:
    """
    See return section.

    :param model_id: model id of the desired FAISS faiss_index artifact in S3
    :return: s3 key of the FAISS faiss_index
    """
    _host: str = host.value
    return f"{_host}-graphs/faiss-index/{_host}_graph_index_voronoi_500_{model_id}.faiss"
