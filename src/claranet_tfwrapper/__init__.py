#!/usr/bin/env python3
"""Python wrapper for Terraform."""

import argcomplete
import argparse
import logging
import os
import pathlib
import pickle
import platform
import random
import re
import shutil
import stat
import string
import subprocess
import tempfile
import textwrap
import time
import shlex
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from urllib3.util.retry import Retry

import boto3
import botocore
import colorlog
import jinja2
import requests
import yaml
from cachecontrol import CacheControlAdapter
from cachecontrol.heuristics import ExpiresAfter
from cachecontrol.caches import FileCache
from natsort import natsorted
from schema import Schema, SchemaError, Optional, Or
from termcolor import colored

from . import azure
from .utils import format_env, get_dict_value

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)


def get_architecture():
    """Get system architecture name normalized for terraform."""
    platform_system = platform.machine()
    if platform_system in ("arm64", "aarch64"):
        return "arm64"
    if platform_system in ("arm", "aarch"):
        return "arm"
    if platform_system in ("amd64", "x86_64"):
        return "amd64"
    return "386"


RC_OK = 0
RC_KO = 1
RC_UNK = 2

LIMIT_GITHUB_RELEASES = 42
GITHUB_RELEASES = "https://github.com/{}/releases"

TERRAFORM_RELEASES_URL = "https://releases.hashicorp.com/terraform/index.json"
TERRAFORM_MINOR_VERSION_REGEX = r"[0-9]+\.[0-9]+"
TERRAFORM_PATCH_REGEX = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"

ARCH_NAME = get_architecture()
PLATFORM_SYSTEM = platform.system().lower()

TFWRAPPER_DEFAULT_CONFIG = {
    "always_trigger_init": False,
    "pipe_plan_command": "cat",
    "use_local_azure_session_directory": True,
}

TERRAFORM_BIN_PATH = None

HOME_DIR = str(Path.home())
DEFAULT_CONF_DIRNAME = "conf"
DEFAULT_HTTP_CACHE_DIR = "{}/.terraform.d/http-cache".format(HOME_DIR)

# setup logging parameters
LOG_FORMAT = "{log_color}{levelname: <7}{reset} {purple}tfwrapper{reset} : {bold}{message}{reset}"
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(LOG_FORMAT, style="{"))
logger = colorlog.getLogger()
logger.addHandler(handler)

stack_configuration_schema = Schema(
    {
        Optional("state_configuration_name"): str,
        Optional("aws"): {"general": {"account": str, "region": str}, "credentials": {"profile": str}},
        Optional("azure"): {
            "general": {"mode": str, "subscription_id": str, "directory_id": str, Optional("credentials"): {"profile": str}},
            Optional(str): {"mode": str, "subscription_id": str, "directory_id": str, Optional("credentials"): {"profile": str}},
            Optional("credential"): {"profile": str},
            Optional("credentials"): {"profile": str},
        },
        Optional("gcp"): {
            "general": {"project": str, "mode": str},
            Optional("gke"): [{Or("zone", "region"): str, "name": str, Optional("refresh_kubeconfig"): Or("always", "never")}],
        },
        "terraform": {"vars": {str: str}, Optional("custom-providers"): {str: Or(str, {"version": str, "extension": str})}},
    }
)


class CachedRequestsSession:
    """
    The python-requests session to use in all HTTP/HTTPS requests.

    It provides caching and retries.
    """

    _session = None
    _file_cache = FileCache(DEFAULT_HTTP_CACHE_DIR)

    def set_cache_dir(cache_dir):
        """Configure requests session's HTTP(S) cache directory."""
        CachedRequestsSession._file_cache.directory = cache_dir

    def get(*args, **kwargs):
        """Wrap requests session's get after having initialized it if needed."""
        if not CachedRequestsSession._session:
            retries = Retry(total=3, backoff_factor=0.3, respect_retry_after_header=True)
            cache_adapter = CacheControlAdapter(
                heuristic=ExpiresAfter(minutes=15),
                cache=CachedRequestsSession._file_cache,
                max_retries=retries,
            )

            session = requests.Session()
            session.mount("http://", cache_adapter)
            session.mount("https://", cache_adapter)

            CachedRequestsSession._session = session
        return CachedRequestsSession._session.get(*args, **kwargs)


def error(message):
    """Raise a ValueError with an help message appended to the original message."""
    raise ValueError("{}\n\nUse -h to show the help message".format(message))


def detect_config_dir(wrapper_config, dir="."):
    """
    Detect the path to the wrapper config directory relative to the provided directory, \
    defaulting to the current working directory.

    Updates the dict passed as a parameter.
    Returns the number of directories traversed.
    """
    parents_count = 0
    while parents_count < 5:
        if os.path.isdir("{}/".format(dir) + "../" * parents_count + wrapper_config["confdir"]):
            wrapper_config["confdir"] = "../" * parents_count + wrapper_config["confdir"]
            logger.debug("Detected confdir at '{}'".format(wrapper_config["confdir"]))
            break
        parents_count += 1

    if parents_count == 5:
        logger.debug(
            "Cannot find configuration directory '{}' in this directory or any of its parents up to 4 levels up".format(
                wrapper_config["confdir"]
            )
        )
        parents_count = 0

    wrapper_config["rootdir"] = os.path.dirname(os.path.abspath("{}/".format(dir) + wrapper_config["confdir"]))
    logger.debug("Detected rootdir at '{}' with {} parents from {}".format(wrapper_config["rootdir"], parents_count, dir))

    return parents_count


def detect_stack(wrapper_config, parents_count, *, raise_on_missing=True, dir="."):
    """
    Detect the stack from the provided directory, defaulting to the current working directory.

    By default, raises an error if any component required to identify a specific stack is missing.
    Updates the dict passed as a parameter.
    """
    # detect parent dirs
    count_up = 0
    count_down = parents_count

    # check wether we are in global environment
    if (
        os.path.basename(os.path.abspath(dir)) == "_global"
        or os.path.basename(os.path.abspath("{}/..".format(dir))) == "_global"
        or wrapper_config["environment"] == "global"
    ):
        parents_list = ["account", "environment", "stack"]
    else:
        parents_list = ["account", "environment", "region", "stack"]

    # detect dirs
    while count_down > 0:
        if wrapper_config[parents_list[count_up]] is None:
            wrapper_config[parents_list[count_up]] = os.path.basename(
                os.path.abspath("{}/".format(dir) + "../" * (count_down - 1))
            )
            # support both _global (fs) and global (param)
            if parents_list[count_up] == "environment" and wrapper_config[parents_list[count_up]] == "_global":
                wrapper_config[parents_list[count_up]] = "global"
            logger.debug("Detected {} '{}'".format(parents_list[count_up], wrapper_config[parents_list[count_up]]))
        count_down -= 1
        count_up += 1

    if raise_on_missing:
        for element in parents_list:
            if wrapper_config[element] is None:
                error("{} cannot be autodetected. Exiting...".format(element))


def load_wrapper_config(wrapper_config):
    """
    Load wrapper and state config from args.

    Validate args and autodetect current stack.
    Updates the dict passed as a parameter.
    """
    # load wrapper config
    wrapper_config_file = os.path.join(wrapper_config["confdir"], "config.yml")
    wrapper_config["config"] = deepcopy(TFWRAPPER_DEFAULT_CONFIG)
    if os.path.exists(wrapper_config_file):
        with open(wrapper_config_file, "r") as f:
            logger.debug("Loading wrapper config from '{}'".format(wrapper_config_file))
            w_config = yaml.safe_load(f)
            if w_config:
                wrapper_config["config"].update(w_config)

    # load state configuration
    config_file = os.path.join(wrapper_config["confdir"], "state.yml")
    state_config = None
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            logger.debug("Loading state config from '{}'".format(config_file))
            state_config = yaml.safe_load(f)
    else:
        logger.debug("No state config file '{}'".format(config_file))

    wrapper_config["state"] = {}
    if state_config is None:
        logger.debug("Empty state config file '{}'".format(config_file))
        return

    for config_type, config in state_config.items():
        if config_type == "backend_parameters":
            continue
        normalized_config = [config] if isinstance(config, dict) else config
        for config in normalized_config:
            config_name = config.get("name", config_type)
            wrapper_config["state"][config_name] = config["general"]
            wrapper_config["state"][config_name].update(
                {
                    # Global
                    "state_backend_type": config_type,
                    "state_backend_parameters": state_config.get("backend_parameters", {}),
                    # Azure configuration
                    "state_subscription": get_dict_value(config, "general", "subscription_id")
                    or get_dict_value(config, "general", "subscription_uid"),
                    "state_rg": get_dict_value(config, "general", "resource_group_name"),
                    "state_storage": get_dict_value(config, "general", "storage_account_name"),
                    # AWS configuration
                    "state_account": get_dict_value(config, "general", "account"),
                    "state_region": get_dict_value(config, "general", "region"),
                    "state_profile": get_dict_value(config, "credentials", "profile"),
                }
            )

    # The default backend is the first in the list
    wrapper_config["default_state_backend_type"] = next(iter(state_config), None)


def get_stack_dir(rootdir, account, environment, region, stack):
    """
    Get the path to a stack given its components.

    Returns the stack dir.
    """
    if environment == "global":
        return "{}/{}/_global/{}".format(rootdir, account, stack)

    if all([rootdir, account, environment, region, stack]):
        return "{}/{}/{}/{}/{}".format(rootdir, account, environment, region, stack)

    return rootdir


def get_stack_config_filename(account, environment, region, stack):
    """
    Get the configuration filename of a stack given its components.

    Returns the stack config path.
    """
    if environment == "global":
        return "{}_global_{}.yml".format(account, stack)
    return "{}_{}_{}_{}.yml".format(account, environment, region, stack)


def get_stack_config_path(confdir, account, environment, region, stack):
    """
    Get the path to a stack configuration file given its components.

    Returns the stack config path.
    """
    return "{}/{}".format(confdir, get_stack_config_filename(account, environment, region, stack))


def get_stack_from_config_path(config_path):
    """
    Get the components of a stack given its configuration file path.

    Returns the stack components.
    """
    config_path_regex = r"(?P<confdir>.+)/(?P<account>[^/_]+)_(?P<environment>[^/_]+)(_(?P<region>[^/_]+))?_(?P<stack>[^/_]+).yml"
    m = re.match(config_path_regex, config_path)
    if not m:
        error("Failed to parse configuration filename {}. Exiting...".format(config_path))

    return m.group("account", "environment", "region", "stack")


def foreach_select_stacks(wrapper_config):
    """
    Select the stacks to process with foreach. Treats unset stack components as wildcard.

    :param wrapper_config: dict: the wrapper config
    :return dict: stack_path => stack_config
    """
    account = wrapper_config["account"] if wrapper_config["account"] else "*"
    environment = wrapper_config["environment"] if wrapper_config["environment"] else "*"
    region = wrapper_config["region"] if wrapper_config["region"] else "*"
    stack = wrapper_config["stack"] if wrapper_config["stack"] else "*"

    pattern = get_stack_config_filename(account, environment, region, stack)
    logger.debug("Selecting stacks matching pattern '{}'".format(pattern))
    stacks = list(pathlib.Path(wrapper_config["confdir"]).glob(pattern))

    if environment == "*" and region == "*":
        # Also select global stacks
        environment = "global"
        pattern = get_stack_config_filename(account, environment, region, stack)
        logger.debug("Also selecting stacks matching pattern '{}'".format(pattern))
        stacks.extend(list(pathlib.Path(wrapper_config["confdir"]).glob(pattern)))

    stacks = sorted(list(stacks), key=lambda stack: str(stack))

    filtered_stacks = {}
    for stack_config in stacks:
        logger.debug("Processing stack config {}".format(stack_config))
        stack = get_stack_from_config_path(str(stack_config))
        stack_dir = get_stack_dir(wrapper_config["rootdir"], *stack)
        if not pathlib.Path(stack_dir).is_dir():
            logger.warning("Stack config {} has no matching directory at {}, skipping.".format(stack_config, stack_dir))
            continue
        logger.debug("Added stack {} => {}".format(stack_dir, stack_config))
        filtered_stacks[stack_dir] = load_stack_config_from_file(stack_config)

    return filtered_stacks


def load_stack_config_from_file(stack_config_file):
    """Load configuration from YAML file."""
    if not os.path.exists(stack_config_file):
        logger.debug("Stack configuration file does not exist: {}".format(stack_config_file))
        return {}

    with open(stack_config_file, "r") as f:
        stack_config = yaml.safe_load(f)

    try:
        stack_configuration_schema.validate(stack_config)
    except SchemaError as e:
        logger.error("Configuration error in {} : {}".format(stack_config_file, e))
        sys.exit(RC_KO)

    return stack_config


def get_stack_envvars(stack_config, wrapper_stack_config):
    """Generate TFWRAPPER environment variables to export."""
    envvars = {}

    for k, v in stack_config.get("terraform").get("vars").items():
        envvars["TFWRAPPER_TF_{}".format(k)] = v

    for v in ("account", "environment", "region", "stack"):
        envvars["TFWRAPPER_{}".format(v)] = wrapper_stack_config.get(v) or ""

    logger.debug("Environment variables generated: {}".format(envvars))
    return {**envvars, **os.environ}


def _get_aws_session(session_cache_file, region, profile):
    """Get or create boto cached session."""
    if os.path.isfile(session_cache_file) and time.time() - os.stat(session_cache_file).st_mtime < 2700:
        with open(session_cache_file, "rb") as f:
            session_cache = pickle.load(f)
        session = boto3.Session(
            aws_access_key_id=session_cache["credentials"].access_key,
            aws_secret_access_key=session_cache["credentials"].secret_key,
            aws_session_token=session_cache["credentials"].token,
            region_name=session_cache["region"],
        )
    else:
        try:
            session = boto3.Session(profile_name=profile, region_name=region)
        except botocore.exceptions.ProfileNotFound:
            logger.error("Profile {} not found. Exiting...".format(profile))
            sys.exit(RC_KO)
        try:
            session_cache = {
                "credentials": session.get_credentials().get_frozen_credentials(),
                "region": session.region_name,
            }
        except botocore.exceptions.ParamValidationError:
            logger.error("Error validating authentication. Maybe the wrong MFA code ?")
            sys.exit(RC_KO)
        except Exception:
            logger.exception("Unknown error")
            sys.exit(RC_UNK)
        with os.fdopen(os.open(session_cache_file, os.O_WRONLY | os.O_CREAT, mode=0o600), "wb") as f:
            pickle.dump(session_cache, f, pickle.HIGHEST_PROTOCOL)
    return session


def get_session(wrapper_config, account, region, profile, backend_type=None, conf=None):
    """Get/create session credentials for supported providers."""
    if backend_type == "aws":
        # Get or create boto cached session.
        session_cache_file = "{}/.run/session_cache_{}_{}.pickle".format(wrapper_config["rootdir"], account, profile)
        session = _get_aws_session(session_cache_file, region, profile)
    elif backend_type == "azure":
        try:
            session = azure.set_context(
                wrapper_config, conf["state_subscription"], None, "", sp_profile=profile, backend_context=True
            )
        except azure.AzureError as e:
            logger.error(f"Error while configuring Azure context: {e.message}")
            exit(RC_KO)
    else:
        session = None

    return session


def set_terraform_vars(vars):
    """Configure Terraform env."""
    for var, value in vars.items():
        if value is not None:
            os.environ["TF_VAR_{}".format(var)] = str(value)


def bootstrap(wrapper_config):
    """Bootstrap project."""
    rootdir = wrapper_config["rootdir"]
    account = wrapper_config["account"]
    environment = wrapper_config["environment"]
    region = wrapper_config["region"]
    stack = wrapper_config["stack"]
    stack_config = wrapper_config["stack_config"]

    stack_path = get_stack_dir(rootdir, account, environment, region, stack)

    state_backend_name = stack_config.get("state_configuration_name", None)
    state_backend_type = (
        wrapper_config["state"].get(state_backend_name)["state_backend_type"]
        if state_backend_name
        else wrapper_config.get("default_state_backend_type", None)
    )
    if state_backend_name:
        logger.info(f'Using state "{state_backend_name}" of type "{state_backend_type}"')
    else:
        logger.info(f'Using state "{state_backend_type}" backend type')

    # get stack cloud provider type
    stack_type = None
    for cloud_provider in ["aws", "azure", "gcp"]:
        if cloud_provider in stack_config:
            stack_type = cloud_provider
            break

    if stack_type is None:
        logger.info("No cloud provider specified in stack configuration.")

    # bootstrap Terraform files from stack template
    if not os.path.isdir(stack_path) or len(os.listdir(path=stack_path)) == 0:
        if wrapper_config.get("template") or stack_type:
            if wrapper_config.get("template"):
                template = wrapper_config["template"].lower()
            else:
                if environment == "global":
                    template = "{}/global".format(stack_type)
                else:
                    template = "{}/basic".format(stack_type)

            # shutil.copytree()'s dirs_exist_ok is new in python 3.8
            if os.path.isdir(stack_path):
                os.rmdir(stack_path)
            template_path = template if os.path.isdir(template) else f"{rootdir}/templates/{template}"
            shutil.copytree(template_path, stack_path, ignore=shutil.ignore_patterns("state.tf", ".terraform"))
            logger.info("Bootstrapped stack using template {}.".format(template))
        else:
            logger.info("No template specified and no cloud provider defined in configuration, skipping.")
            os.makedirs(stack_path, exist_ok=True)
    else:
        logger.info(
            "Stack path {} already exists and is not empty, skipping stack bootstrapping from template.".format(stack_path)
        )

    # bootstrap state.tf from jinja2 template with a specified backend
    if not os.path.isfile("{}/state.tf".format(stack_path)):
        if state_backend_type:
            client_name = stack_config["terraform"]["vars"].get("client_name", account)

            template_path = "{}/templates/{}/common".format(rootdir, state_backend_type)
            logger.debug("Using template path {}".format(template_path))

            jinja2_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_path),
                lstrip_blocks=True,
                trim_blocks=True,
            )

            state_yml_parameters = wrapper_config["state"].get(state_backend_name or state_backend_type) or next(
                iter(wrapper_config["state"])
            )
            logger.debug("Parameters from state.yml: {}".format(state_yml_parameters))

            state_conf = jinja2_env.get_template("state.tf.jinja2").render(
                client_name=client_name,
                account=account,
                environment=environment,
                region=region,
                stack=stack,
                state_parameters=state_yml_parameters,
            )

            with open("{}/state.tf".format(stack_path), "w") as f:
                f.write(state_conf)

            logger.info('Generated state.tf file with "{}" backend type configured.'.format(state_backend_type))
            logger.info("Run `tfwrapper init` to initialize this new stack.")
        else:
            logger.warning("No state backend configuration found, skipping state configuration file state.tf generation.")
    else:
        logger.warning("State configuration file state.tf already exists, skipping its generation.")


def search_on_github(repo, minor_version, patch_regex, patch):
    """Search release on github."""
    # Start search from the next incremented minor version
    # Note: the github UI serves the first page if the requested version does not exist
    release = "v{}{}.0".format(minor_version[:-1], int(minor_version[-1]) + 1)
    releases_count = 0
    while True:
        result = CachedRequestsSession.get("{}?after={}".format(GITHUB_RELEASES.format(repo), release))
        releases = re.findall(r"<a href=\"/{}/releases/tag/.*\">(.*)</a>".format(repo), result.text)
        releases_count += len(releases)
        for release in releases:
            logger.debug(
                'Release found: "{}", checking with "^v{}.{}$"'.format(release, minor_version, patch if patch else patch_regex)
            )
            if re.match(
                r"^v{}\.{}$".format(minor_version, patch if patch else patch_regex),
                release,
            ):
                patch = patch or release.split(".")[-1]
                return patch
            # hard limit or it will take too long
            if releases_count > LIMIT_GITHUB_RELEASES:
                return None
        if len(releases) < 1:
            # no more version available
            break

        release = releases[-1:][0]
    return None


def get_terraform_last_patch(minor_version):
    """Get last terraform patch of a given minor version."""
    releases = CachedRequestsSession.get(TERRAFORM_RELEASES_URL).json()
    if type(releases) is dict and type(releases["versions"]) is dict:
        # Use recommended sorting method to place releases before all pre-versions from
        # https://natsort.readthedocs.io/en/master/examples.html#sorting-more-expressive-versioning-schemes
        for release in natsorted(releases["versions"].keys(), key=lambda x: x.replace(".", "~") + "z", reverse=True):
            if re.match(r"^{}\.{}$".format(minor_version, TERRAFORM_PATCH_REGEX), release):
                logger.debug("Found {} for {}".format(release, minor_version))
                return release.split(".")[-1]

        raise ValueError("The terraform minor version {} does not exist".format(minor_version))

    message = releases.get("message", "Unknown error")
    logger.warning("Failed to retrieve terraform releases from {}: {}".format(TERRAFORM_RELEASES_URL, message))

    return None


def select_terraform_version(version):
    """
    Select the desired terraform version.

    :param version: string: desired terraform version
    """
    m = re.match(
        r"^(?P<minor>{})(\.(?P<patch>{}))?$".format(TERRAFORM_MINOR_VERSION_REGEX, TERRAFORM_PATCH_REGEX),
        version,
    )
    if not m:
        error('The terraform version seems not correct, it should be a version number like "X.Y" or "X.Y.Z"')
    minor_version, patch, dev = m.group("minor", "patch", "dev")

    # Getting latest patch version if not defined
    if not patch:
        patch = get_terraform_last_patch(minor_version)
    full_version = "{}.{}".format(minor_version, patch)

    version_path = os.path.expanduser(os.path.join("~/.terraform.d/versions", minor_version, full_version))
    global TERRAFORM_BIN_PATH
    TERRAFORM_BIN_PATH = os.path.join(version_path, "terraform")
    os.makedirs(version_path, exist_ok=True)

    if not os.path.isfile(TERRAFORM_BIN_PATH):
        if patch.endswith("-dev"):
            error("The development version {} for terraform does not exist locally".format(version))

        if PLATFORM_SYSTEM == "darwin" and ARCH_NAME == "arm64" and full_version < "1.0.2":
            arch = "amd64"
            logger.warning(
                "Terraform only supports darwin (MacOS) on arm64 (Apple Silicon M1) since v1.0.2, "
                "so force usage of {} binaries with Rosetta on darwin for older terraform versions".format(arch)
            )
        else:
            arch = ARCH_NAME

        # Download and extract in user's home if needed
        logger.warning("Terraform version {} does not exist locally, downloading it".format(full_version))
        handle, tmp_file = tempfile.mkstemp(prefix="terraform-", suffix=".zip")
        r = CachedRequestsSession.get(
            "https://releases.hashicorp.com/terraform/{full_version}/terraform_{full_version}_{platform}_{arch}.zip".format(
                full_version=full_version, platform=PLATFORM_SYSTEM, arch=arch
            ),
            stream=True,
        )
        if r.status_code != 200:
            raise ValueError(
                "Failed to download terraform version {}, it probably does not exist: {}".format(full_version, r.status_code)
            )

        with open(tmp_file, "wb") as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        with zipfile.ZipFile(tmp_file, "r") as zip:
            zip.extractall(path=version_path)
        # Permissions not preserved on extract https://bugs.python.org/issue15795
        os.chmod(
            TERRAFORM_BIN_PATH,
            os.stat(TERRAFORM_BIN_PATH).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
        )
        os.remove(tmp_file)

    logger.info("Using terraform version {}".format(full_version))


def download_custom_provider(provider_name, provider_version, extension="zip"):
    """Download Terraform custom provider."""
    logger.info("Checking custom Terraform provider '{}' at version '{}'".format(provider_name, provider_version))
    github_base = "https://github.com/"
    github_endpoint = "{g}{p}".format(g=github_base, p=provider_name)
    supported_extensions = ["zip", "tar.gz", "tar.bz2"]

    if extension not in supported_extensions:
        error("Extension {} is not supported. Only {} are.".format(extension, ", ".join(supported_extensions)))

    r = CachedRequestsSession.get(github_endpoint)
    if r.status_code != 200:
        error("The terraform provider {} does not exist ({})".format(provider_name, github_endpoint))

    m = re.match(r"^v?([0-9]+.[0-9]+).?([0-9]+)?(-[a-z0-9]+)?$", provider_version)
    if not m:
        error(
            'The provider version does not seem correct, it should be a version number like "X.Y", "X.Y.Z" or ' '"X.Y.Z-custom"'
        )
    minor_version, patch, custom = m.groups()

    patch = search_on_github(provider_name, minor_version, r"[0-9]+(-[a-z0-9_-]+)?", patch)

    if not patch:
        error("The provider version '{}-{}' does not exist".format(provider_name, provider_version))

    full_version = "{}.{}".format(minor_version, patch)

    # Getting current version
    plugins_path = os.path.expanduser("~/.terraform.d/plugins/{platform}_{arch}".format(platform=PLATFORM_SYSTEM, arch=ARCH_NAME))
    os.makedirs(plugins_path, exist_ok=True)
    provider_short_name = provider_name.split("/", 1)[1]
    bin_name = "{n}_{v}".format(n=provider_short_name, v=full_version)
    if provider_version.startswith("v"):
        # Do it now so we keep full_version clean for building url
        bin_name = "{n}_v{v}".format(n=provider_short_name, v=full_version)
    else:
        bin_name = "{n}_{v}".format(n=provider_short_name, v=full_version)
    TERRAFORM_BIN_PATH = os.path.join(plugins_path, "{n}_v{v}".format(n=provider_short_name, v=full_version))

    if not os.path.isfile(TERRAFORM_BIN_PATH):
        # Download and extract in user's home if needed
        logger.warning("Provider version does not exist locally, downloading it")
        handle, tmp_file = tempfile.mkstemp(prefix="terraform-", suffix="." + extension)
        r = CachedRequestsSession.get(
            "https://github.com/{p}/releases/download/v{v}/{b}_{platform}_{arch}.{extension}".format(
                p=provider_name,
                v=full_version,
                b=bin_name,
                platform=PLATFORM_SYSTEM,
                arch=ARCH_NAME,
                extension=extension,
            ),
            stream=True,
        )
        with open(tmp_file, "wb") as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        shutil.unpack_archive(tmp_file, plugins_path)
        # Permissions not preserved on extract https://bugs.python.org/issue15795
        os.chmod(
            TERRAFORM_BIN_PATH,
            os.stat(TERRAFORM_BIN_PATH).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
        )
        os.remove(tmp_file)
        logger.info("Download done, current provider version is {}".format(full_version))
    else:
        logger.debug("Current provider version is already {}".format(full_version))


def adc_check_gke_credentials(
    adc_path,
    kubeconfig_path,
    gke_name,
    project,
    zone=None,
    region=None,
    refresh_kubeconfig=None,
):
    """Provision kubeconfig for a given GKE instance using ADC."""
    gke_env = {
        "CLOUDSDK_CONTAINER_USE_APPLICATION_DEFAULT_CREDENTIALS": "true",
        "CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE": adc_path,
        "KUBECONFIG": kubeconfig_path,
    }
    cmd_env = deepcopy(os.environ)
    cmd_env.update(gke_env)

    logger.info("Looking for {} GKE credentials.".format(gke_name))

    if zone is not None:
        command = [
            "gcloud",
            "container",
            "clusters",
            "get-credentials",
            gke_name,
            "--project",
            project,
            "--zone",
            zone,
        ]
    elif region is not None:
        command = [
            "gcloud",
            "container",
            "clusters",
            "get-credentials",
            gke_name,
            "--project",
            project,
            "--region",
            region,
        ]
    else:
        logger.error("You must specify a zone or region for {} GKE instance.".format(gke_name))
        sys.exit(RC_KO)

    if refresh_kubeconfig not in ["always", "never"]:
        logger.error('refresh_kubeconfig must be one of "always", "never" but is {}'.format(refresh_kubeconfig))
        sys.exit(RC_KO)

    logger.debug("Using kubeconfig path {} .".format(kubeconfig_path))
    if refresh_kubeconfig == "always" or not Path(kubeconfig_path).is_file():
        logger.info("Refreshing {} GKE credentials.".format(gke_name))
        try:
            logger.debug("Executing `{} {}`".format(format_env(gke_env), " ".join(command)))
            subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                env=cmd_env,
            )
        except subprocess.CalledProcessError as e:
            logger.error(
                "Could not configure {} GKE credentials, the following command failed:\n\n"
                "    {} {}\n\n"
                "with the following error:\n\n"
                "{}".format(gke_name, format_env(gke_env), " ".join(command), textwrap.indent(e.output.decode(), "    "))
            )

            sys.exit(RC_KO)
        logger.info("{} GKE credentials configured.".format(gke_name))
    else:
        logger.info("Using existing {} kubeconfig file.".format(gke_name))


def run_terraform(action, wrapper_config):
    """Run Terraform command."""
    rootdir = wrapper_config["rootdir"]

    tf_params = wrapper_config.get("tf_params")
    account = wrapper_config["account"]
    environment = wrapper_config["environment"]
    region = wrapper_config["region"]
    stack = wrapper_config["stack"]

    # support for custom parameters
    command = [TERRAFORM_BIN_PATH, action]

    if action == "init" and not wrapper_config["backend"]:
        command.append("-backend=false")

    if tf_params is not None:
        if tf_params and tf_params[0] == "--":
            tf_params = tf_params[1:]
        command += tf_params

    working_dir = get_stack_dir(rootdir, account, environment, region, stack)

    pipe_plan_command = wrapper_config.get("pipe_plan_command") or wrapper_config["config"].get("pipe_plan_command")
    pipe_plan = action == "plan" and wrapper_config.get("pipe_plan") and pipe_plan_command
    stdout = pipe_plan and subprocess.PIPE or None
    with subprocess.Popen(command, cwd=working_dir, env=os.environ, shell=False, stdout=stdout) as process:
        logger.debug('Execute command "{}"'.format(command))
        if pipe_plan:
            logger.debug('Piping command "{}"'.format(pipe_plan_command))
            with subprocess.Popen(
                pipe_plan_command,
                cwd=working_dir,
                env=os.environ,
                shell=True,
                stdin=process.stdout,
            ) as pipe_process:
                try:
                    pipe_process.communicate()
                except KeyboardInterrupt:
                    logger.warning("Received Ctrl+C")
                except:  # noqa
                    pipe_process.kill()
                    pipe_process.wait()
                    raise
                pipe_process.poll()
        try:
            process.communicate()
        except KeyboardInterrupt:
            logger.warning("Received Ctrl+C")
        except:  # noqa
            process.kill()
            process.wait()
            raise
        return process.poll()


def terraform_apply(wrapper_config):
    """Terraform apply wrapper function."""
    always_trigger_init = wrapper_config["config"].get("always_trigger_init", False)
    logger.debug("Checking 'always_trigger_init' option: {}".format(always_trigger_init))
    if always_trigger_init:
        logger.info("Init has been activated in config")
        terraform_init(wrapper_config)

    # do not force plan if unsafe
    if wrapper_config["unsafe"]:
        return run_terraform("apply", wrapper_config)
    else:
        # plan config
        plan_path = "{}/.run/plan_{}".format(
            wrapper_config["rootdir"],
            "".join(random.choice(string.ascii_letters) for x in range(10)),
        )
        plan_wrapper_config = deepcopy(wrapper_config)
        plan_wrapper_config["tf_params"][1:1] = ["-out", plan_path]
        plan_return_code = run_terraform("plan", plan_wrapper_config)

        # return Terraform return code if plan fails
        if plan_return_code > 0:
            return plan_return_code

        # ask for confirmation
        colored_account = colored(plan_wrapper_config["account"], "yellow")
        colored_environment = colored(plan_wrapper_config["environment"], "red")
        colored_region = colored(plan_wrapper_config["region"], "blue")
        colored_stack = colored(plan_wrapper_config["stack"], "green")

        if plan_wrapper_config["environment"] == "global":
            env_msg = """
    Account : {}
Environment : {}
      Stack : {}
""".format(
                colored_account, colored_environment, colored_stack
            )
        else:
            env_msg = """
    Account : {}
Environment : {}
     Region : {}
      Stack : {}
""".format(
                colored_account, colored_environment, colored_region, colored_stack
            )

        print(
            "\nDo you really want to apply this plan on the following stack ?\n",
            env_msg,
        )
        apply_input = input("'yes' to confirm: ")

        try:
            if apply_input == "yes":
                # apply config
                apply_wrapper_config = deepcopy(wrapper_config)
                apply_wrapper_config["tf_params"].append(plan_path)
                apply_return_code = run_terraform("apply", apply_wrapper_config)

                return apply_return_code
            else:
                logger.warning("Aborting apply.")
        finally:
            # delete plan
            os.remove(plan_path)


def terraform_console(wrapper_config):
    """Terraform console wrapper function."""
    return run_terraform("console", wrapper_config)


def terraform_destroy(wrapper_config):
    """Terraform destroy wrapper function."""
    return run_terraform("destroy", wrapper_config)


def terraform_fmt(wrapper_config):
    """Terraform fmt wrapper function."""
    return run_terraform("fmt", wrapper_config)


def terraform_force_unlock(wrapper_config):
    """Terraform force-unlock wrapper function."""
    return run_terraform("force-unlock", wrapper_config)


def terraform_get(wrapper_config):
    """Terraform get wrapper function."""
    # force update
    if not any("-update" in x for x in wrapper_config["tf_params"]):
        wrapper_config["tf_params"][1:1] = ["-update"]

    # call subcommand
    return run_terraform("get", wrapper_config)


def terraform_graph(wrapper_config):
    """Terraform graph wrapper function."""
    return run_terraform("graph", wrapper_config)


def terraform_import(wrapper_config):
    """Terraform import wrapper function."""
    return run_terraform("import", wrapper_config)


def terraform_init(wrapper_config):
    """Terraform init wrapper function."""
    return run_terraform("init", wrapper_config)


def terraform_output(wrapper_config):
    """Terraform output wrapper function."""
    return run_terraform("output", wrapper_config)


def terraform_plan(wrapper_config):
    """Terraform plan wrapper function."""
    always_trigger_init = wrapper_config["config"].get("always_trigger_init", False)
    logger.debug("Checking 'always_trigger_init' option: {}".format(always_trigger_init))
    if always_trigger_init:
        logger.info("Init has been activated in config")
        terraform_init(wrapper_config)
    return run_terraform("plan", wrapper_config)


def terraform_providers(wrapper_config):
    """Terraform providers wrapper function."""
    return run_terraform("providers", wrapper_config)


def terraform_refresh(wrapper_config):
    """Terraform refresh wrapper function."""
    return run_terraform("refresh", wrapper_config)


def terraform_show(wrapper_config):
    """Terraform show wrapper function."""
    return run_terraform("show", wrapper_config)


def terraform_state(wrapper_config):
    """Terraform state wrapper function."""
    return run_terraform("state", wrapper_config)


def terraform_taint(wrapper_config):
    """Terraform taint wrapper function."""
    return run_terraform("taint", wrapper_config)


def terraform_untaint(wrapper_config):
    """Terraform untaint wrapper function."""
    return run_terraform("untaint", wrapper_config)


def terraform_validate(wrapper_config):
    """Terraform validate wrapper function."""
    return run_terraform("validate", wrapper_config)


def terraform_version(wrapper_config):
    """Terraform version wrapper function."""
    return run_terraform("version", wrapper_config)


def terraform_workspace(wrapper_config):
    """Terraform workspace wrapper function."""
    return run_terraform("workspace", wrapper_config)


def foreach(wrapper_config):
    """Execute command foreach stack."""
    stacks = foreach_select_stacks(wrapper_config)
    for stack, stack_config in stacks.items():
        command = wrapper_config["command"]
        shell = wrapper_config["shell"]
        executable = wrapper_config["executable"]

        wrapper_stack_config = deepcopy(wrapper_config)
        wrapper_stack_config["confdir"] = "conf/"
        parents_count = detect_config_dir(wrapper_stack_config, dir=stack)
        detect_stack(wrapper_stack_config, parents_count, raise_on_missing=True, dir=stack)
        stack_env = get_stack_envvars(stack_config, wrapper_stack_config)

        with subprocess.Popen(command, cwd=stack, shell=shell, executable=executable, env=stack_env) as process:
            logger.debug('Execute command "{}" in "{}"'.format(command, stack))
            try:
                process.communicate()
            except KeyboardInterrupt:
                logger.warning("Received Ctrl+C")
            except:  # noqa
                process.kill()
                process.wait()
                raise
            returncode = process.poll()
            if returncode != 0:
                # TODO: add option to collect errors and report at end?
                return returncode
    return 0


def terraform_completer(prefix, action, parser, parsed_args):
    """Get completions for terraform command line arguments."""
    logger.debug(
        "terraform_completer(prefix={}, action={}, parser={}, parsed_args={})".format(prefix, action, parser, parsed_args)
    )

    working_dir = "."
    command = [TERRAFORM_BIN_PATH]
    # Pass environment variables unchanged, including COMP_LINE which is defined by the shell
    # when invoked during auto-completion
    logger.debug('Execute command "{}" with environment {}'.format(command, os.environ))
    process = subprocess.run(
        command, cwd=working_dir, env=os.environ, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="ascii"
    )
    return sorted(process.stdout.strip().split("\n"))


def parse_base_args(args):
    """Parse -d/--debug command line argument and setup HTTP cache dir."""
    # Get command line arguments from COMP_LINE environment variable which is defined by the shell
    # when invoked during auto-completion
    if not args and "COMP_LINE" in os.environ:
        args = shlex.split(os.environ["COMP_LINE"])

    parser = argparse.ArgumentParser(
        prog="tfwrapper",
        add_help=False,
    )
    parser.add_argument("-d", "--debug", action="store_true", default=False)
    parser.add_argument("-c", "--confdir", nargs="?", const=DEFAULT_CONF_DIRNAME, default=DEFAULT_CONF_DIRNAME)
    parser.add_argument("-a", "--account", nargs="?")
    parser.add_argument("-e", "--environment", nargs="?")
    parser.add_argument("-r", "--region", nargs="?")
    parser.add_argument("-s", "--stack", nargs="?")
    parser.add_argument("--http-cache-dir", nargs="?", const=DEFAULT_HTTP_CACHE_DIR, default=DEFAULT_HTTP_CACHE_DIR)
    parsed_args, _ = parser.parse_known_args(args)

    logger.setLevel(logging.DEBUG if parsed_args.debug else logging.INFO)

    # configure requests session's cache directory
    CachedRequestsSession.set_cache_dir(parsed_args.http_cache_dir)

    return parsed_args


def parse_args(args):
    """Parse command line arguments."""
    # terraform params doc
    confdir_help = "Configuration directory. Used to detect the project root. Defaults to conf."
    target_help = "Target {}. Autodetected if none is provided."
    tf_params_help = 'Any Terraform parameters after a "--" delimiter'

    # argparse
    parser = argparse.ArgumentParser(
        prog="tfwrapper",
        description="Terraform wrapper.",
        argument_default=argparse.SUPPRESS,
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output.")
    parser.add_argument("-V", "--version", action="store_true", default=False, help="Show tfwrapper version.")
    parser.add_argument("-c", "--confdir", help=confdir_help)
    parser.add_argument("-a", "--account", help=target_help.format("account"), nargs="?")
    parser.add_argument("-e", "--environment", help=target_help.format("environment"), nargs="?")
    parser.add_argument("-r", "--region", help=target_help.format("region"), nargs="?")
    parser.add_argument("-s", "--stack", help=target_help.format("stack"), nargs="?")
    parser.add_argument("--http-cache-dir", help="HTTP(S) requests cache directory.")
    parser.add_argument(
        "-p",
        "--plugin-cache-dir",
        help="Plugins cache directory.",
        default=os.environ.get("TF_PLUGIN_CACHE_DIR", "{}/.terraform.d/plugin-cache".format(HOME_DIR)),
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="subcommands")

    parser_apply = subparsers.add_parser("apply", help="terraform apply")
    parser_apply.set_defaults(func=terraform_apply)
    parser_apply.add_argument(
        "-u",
        "--unsafe",
        help="Do not force plan and human interaction before apply.",
        action="store_true",
        default=False,
    )
    parser_apply.add_argument(
        "-l",
        "--pipe-plan",
        action="store_true",
        default=False,
        help=("Pipe plan output to the command set in config" " or passed in --pipe-plan-command argument (cat by default)."),
    )
    parser_apply.add_argument(
        "--pipe-plan-command",
        action="store",
        nargs="?",
        help="Pipe plan output to the command of your choice set as argument inline value.",
    )
    parser_apply.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_console = subparsers.add_parser("console", help="terraform console")
    parser_console.set_defaults(func=terraform_console)
    parser_console.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_destroy = subparsers.add_parser("destroy", help="terraform destroy")
    parser_destroy.set_defaults(func=terraform_destroy)
    parser_destroy.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_fmt = subparsers.add_parser("fmt", help="terraform fmt")
    parser_fmt.set_defaults(func=terraform_fmt)
    parser_fmt.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_force_unlock = subparsers.add_parser("force-unlock", help="terraform force-unlock")
    parser_force_unlock.set_defaults(func=terraform_force_unlock)
    parser_force_unlock.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help)

    parser_get = subparsers.add_parser("get", help="terraform get")
    parser_get.set_defaults(func=terraform_get)
    parser_get.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_graph = subparsers.add_parser("graph", help="terraform graph")
    parser_graph.set_defaults(func=terraform_graph)
    parser_graph.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_import = subparsers.add_parser("import", help="terraform import")
    parser_import.set_defaults(func=terraform_import)
    parser_import.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_init = subparsers.add_parser("init", help="terraform init")
    parser_init.set_defaults(func=terraform_init)
    parser_init.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer
    parser_init.add_argument(
        "--backend",
        choices=["true", "false"],
        default="true",
        help="configure the backend for this configuration.",
    )

    parser_output = subparsers.add_parser("output", help="terraform output")
    parser_output.set_defaults(func=terraform_output)
    parser_output.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_plan = subparsers.add_parser("plan", help="terraform plan")
    parser_plan.set_defaults(func=terraform_plan)
    parser_plan.add_argument(
        "-l",
        "--pipe-plan",
        action="store_true",
        default=False,
        help=("Pipe plan output to the command set in config" " or passed in --pipe-plan-command argument (cat by default)."),
    )
    parser_plan.add_argument(
        "--pipe-plan-command",
        action="store",
        nargs="?",
        help="Pipe plan output to the command of your choice set as argument inline value.",
    )
    parser_plan.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_providers = subparsers.add_parser("providers", help="terraform providers")
    parser_providers.set_defaults(func=terraform_providers)
    parser_providers.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_refresh = subparsers.add_parser("refresh", help="terraform refresh")
    parser_refresh.set_defaults(func=terraform_refresh)
    parser_refresh.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_show = subparsers.add_parser("show", help="terraform show")
    parser_show.set_defaults(func=terraform_show)
    parser_show.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_state = subparsers.add_parser("state", help="terraform state")
    parser_state.set_defaults(func=terraform_state)
    parser_state.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_taint = subparsers.add_parser("taint", help="terraform taint")
    parser_taint.set_defaults(func=terraform_taint)
    parser_taint.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_untaint = subparsers.add_parser("untaint", help="terraform untaint")
    parser_untaint.set_defaults(func=terraform_untaint)
    parser_untaint.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_validate = subparsers.add_parser("validate", help="terraform validate")
    parser_validate.set_defaults(func=terraform_validate)
    parser_validate.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_version = subparsers.add_parser("version", help="terraform version")
    parser_version.set_defaults(func=terraform_version)
    parser_version.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_workspace = subparsers.add_parser("workspace", help="terraform workspace")
    parser_workspace.set_defaults(func=terraform_workspace)
    parser_workspace.add_argument("tf_params", nargs=argparse.REMAINDER, help=tf_params_help).completer = terraform_completer

    parser_bootstrap = subparsers.add_parser("bootstrap", help="bootstrap configuration")
    parser_bootstrap.set_defaults(func=bootstrap)
    parser_bootstrap.add_argument("template", nargs="?", help="template to use during bootstrap", default=None)

    parser_foreach = subparsers.add_parser("foreach", help="execute command for each stack")
    parser_foreach.set_defaults(func=foreach)
    parser_foreach.add_argument("-S", "--shell", dest="shell", action="store_true", help="execute command in a shell")
    parser_foreach.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help='command to execute after a "--" delimiter',
    )

    argcomplete.autocomplete(parser, exit_method=sys.exit)
    parsed_args = parser.parse_args(args)

    if hasattr(parsed_args, "version") and parsed_args.version:
        print("tfwrapper v{}".format(__version__), file=sys.stderr)
        raise SystemExit(0)

    if not hasattr(parsed_args, "func"):
        parser.print_help(file=sys.stderr)
        raise SystemExit(0)

    if parsed_args.func == foreach:
        if len(parsed_args.command) > 0 and parsed_args.command[0] == "--":
            parsed_args.command = parsed_args.command[1:]
        if len(parsed_args.command) < 1:
            raise ValueError("foreach: error: a command is required")
        if parsed_args.shell and len(parsed_args.command) > 1:
            raise ValueError("foreach: error: -S/--shell must be followed by a single argument (hint: use quotes)")
        parsed_args.executable = os.environ.get("SHELL", None) if parsed_args.shell else None

    return parsed_args


def main(argv=None):
    """Execute tfwrapper.

    Note: there are two execution paths:
    - the nominal one is standard execution where arguments are normally passed in sys.argv.
    - the alternative one is auto-completion execution where _ARGCOMPLETE, COMP_LINE and COMP_POINT
      environment variables are defined, and arguments are passed in COMP_LINE.
    """
    # parse base flags on their own to:
    # - activate debug log level early
    # - setup HTTP cache before downloading terraform index and binaries needed for completion
    args = parse_base_args(argv or sys.argv[1:])
    wrapper_config = deepcopy(vars(args))

    # locate config and root dirs
    parents_count = detect_config_dir(wrapper_config)

    # detect if we are in a stack
    detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    # load wrapper config
    load_wrapper_config(wrapper_config)

    # load stack config
    stack_config_file = get_stack_config_path(
        wrapper_config["confdir"],
        wrapper_config["account"],
        wrapper_config["environment"],
        wrapper_config["region"],
        wrapper_config["stack"],
    )
    stack_config = load_stack_config_from_file(stack_config_file)

    # select terraform version for the stack if selected with a fallback on v1.0
    tf_version = stack_config.get("terraform", {}).get("vars", {}).get("version", "1.0")
    select_terraform_version(tf_version)

    # parse all args
    args = parse_args(argv or sys.argv[1:])

    # convert args to dict
    wrapper_config.update(vars(args))

    # error if stack folder or config are missing for commands requiring them
    wrapper_commands_not_requiring_stack_config = (
        "console",
        "fmt",
        "foreach",
        "providers",
        "validate",
        "version",
    )
    if args.subcommand not in wrapper_commands_not_requiring_stack_config:
        if (
            wrapper_config["environment"] != "global"
            and not all(
                [
                    wrapper_config["account"],
                    wrapper_config["environment"],
                    wrapper_config["region"],
                    wrapper_config["stack"],
                ]
            )
            or not all(
                [
                    wrapper_config["account"],
                    wrapper_config["environment"],
                    wrapper_config["stack"],
                ]
            )
        ):
            logger.error("Cannot determine which stack to target for {}, aborting.".format(args.subcommand))
            sys.exit(RC_KO)

        rootdir = wrapper_config["rootdir"]
        account = wrapper_config["account"]
        environment = wrapper_config["environment"]
        region = wrapper_config["region"]
        stack = wrapper_config["stack"]
        stack_path = get_stack_dir(rootdir, account, environment, region, stack)

        if args.subcommand != "bootstrap" and not os.path.isdir(stack_path):
            logger.error(
                "A valid stack configuration directory {} is required for {} subcommand, aborting.".format(
                    stack_config_file, args.subcommand
                )
            )
            sys.exit(RC_KO)

        if not os.path.exists(stack_config_file):
            logger.error(
                "A valid stack configuration file {} is required for {} subcommand, aborting.".format(
                    stack_config_file, args.subcommand
                )
            )
            sys.exit(RC_KO)

    # pass loaded stack config to bootstrap subcommand
    if args.subcommand == "bootstrap":
        wrapper_config["stack_config"] = stack_config

    # get state backend and stack credentials
    wrapper_local_commands = (
        "bootstrap",
        "foreach",
    )
    if args.subcommand not in wrapper_local_commands:
        # get sessions
        state_backend_name = stack_config.get("state_configuration_name", None)
        load_backend = wrapper_config["backend"] = not (
            (args.subcommand == "init" and args.backend == "false")
            or args.subcommand
            in (
                "fmt",
                "get",
                "providers",
                "test",
                "validate",
                "version",
            )
        )

        if load_backend and wrapper_config["state"]:
            try:
                state_config = (
                    wrapper_config["state"][state_backend_name]
                    if state_backend_name
                    else next(iter(wrapper_config["state"].values()))
                )
            except KeyError:
                logger.error(f'State configuration "{state_backend_name}" does not exist.')
                exit(RC_KO)

            state_backend_type = state_config["state_backend_type"]

            state_session = get_session(
                wrapper_config,
                state_config.get("state_account"),
                state_config.get("state_region"),
                state_config.get("state_profile"),
                state_backend_type,
                state_config,
            )

            if state_backend_type == "aws":
                # set AWS state centralization environment variables
                state_credentials = state_session.get_credentials().get_frozen_credentials()
                os.environ["AWS_ACCESS_KEY_ID"] = state_credentials.access_key
                os.environ["AWS_SECRET_ACCESS_KEY"] = state_credentials.secret_key
                if state_credentials.token:
                    os.environ["AWS_SESSION_TOKEN"] = state_credentials.token
                logger.info("AWS state backend initialized.")
            elif state_backend_type == "azure":
                set_terraform_vars(state_session)
                logger.info("Azure state backend initialized.")
            else:
                logger.info(
                    f'Using state backend type "{state_backend_type}". No custom implementation, let terraform handle '
                    f"with its default behavior."
                )

        terraform_vars = stack_config.get("terraform", {}).get("vars", {})
        terraform_vars["environment"] = wrapper_config["environment"]
        terraform_vars["stack"] = wrapper_config["stack"]
        terraform_vars["account"] = wrapper_config["account"]
        terraform_vars["region"] = wrapper_config["region"]

        # AWS support
        if load_backend and "aws" in stack_config:
            logger.info("Getting stack session")
            stack_session = get_session(
                wrapper_config,
                stack_config["aws"]["general"]["account"],
                stack_config["aws"]["general"]["region"],
                stack_config["aws"]["credentials"]["profile"],
                "aws",
            )

            # set terraform environment variables for AWS Stack
            stack_credentials = stack_session.get_credentials().get_frozen_credentials()
            terraform_vars["aws_access_key"] = stack_credentials.access_key
            terraform_vars["aws_secret_key"] = stack_credentials.secret_key
            terraform_vars["aws_token"] = stack_credentials.token

        # GCP/GKE support
        if load_backend and "gcp" in stack_config:
            gcp_auth_mode = stack_config["gcp"]["general"].get("mode")
            if gcp_auth_mode.lower() == "adc-user":
                # In this mode we are trying to use ADC credentials of type authorized_user.
                # The rational is to facilitate interactive usage from a local dev environment.
                # We assume that the user is using the same identity for all projects.
                # GKE access, if required, is configured using the same credentials with per-stack kuebconfig files.

                logger.info("Looking for GCP user Application Default Credentials.")
                try:
                    command = [
                        "gcloud",
                        "auth",
                        "application-default",
                        "print-access-token",
                    ]
                    logger.debug("Executing `{}`".format(" ".join(command)))
                    subprocess.run(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=True,
                    )
                except FileNotFoundError:
                    logger.error("Please make sure that gcloud is available on this system.")
                    sys.exit(RC_KO)
                except subprocess.CalledProcessError as e:
                    logger.error(
                        "Could not find valid user Application Default Credentials, the following command failed:\n\n"
                        "    {}\n\n"
                        "with the following error:\n\n"
                        "{}\n"
                        "You may need to run:\n\n"
                        "    gcloud auth application-default login".format(
                            " ".join(command), textwrap.indent(e.output.decode(), "    ")
                        )
                    )
                    sys.exit(RC_KO)
                logger.info("Found GCP user Application Default Credentials.")

                if "gke" in stack_config["gcp"]:
                    project = stack_config["gcp"]["general"]["project"]

                    for cluster in stack_config["gcp"]["gke"]:
                        gke_name = cluster["name"]
                        adc_path = os.path.join(
                            os.path.abspath(HOME_DIR),
                            ".config/gcloud/application_default_credentials.json",
                        )
                        kubeconfig_path = "{}/.run/{}_{}_{}_{}_{}.kubeconfig".format(
                            wrapper_config["rootdir"],
                            wrapper_config["account"],
                            wrapper_config["environment"],
                            wrapper_config["region"],
                            wrapper_config["stack"],
                            gke_name,
                        )
                        refresh_kubeconfig = cluster.get("refresh_kubeconfig", "always")
                        if "zone" in cluster:
                            adc_check_gke_credentials(
                                adc_path,
                                kubeconfig_path,
                                gke_name,
                                project,
                                zone=cluster["zone"],
                                refresh_kubeconfig=refresh_kubeconfig,
                            )
                        elif "region" in cluster:
                            adc_check_gke_credentials(
                                adc_path,
                                kubeconfig_path,
                                gke_name,
                                project,
                                region=cluster["region"],
                                refresh_kubeconfig=refresh_kubeconfig,
                            )
                        else:
                            logger.error("You must specify a zone or region for {} GKE instance.".format(gke_name))
                            sys.exit(RC_KO)

                        terraform_vars["gke_kubeconfig_{}".format(gke_name)] = kubeconfig_path
            else:
                logger.error("Sorry, tfwrapper only supports user Application Default Credentials right now.")
                sys.exit(RC_KO)

        # Azure support
        if load_backend and "azure" in stack_config:
            terraform_vars["azurerm_region"] = wrapper_config["region"]  # Kept for backwards compatibility
            terraform_vars["azure_region"] = wrapper_config["region"]

            for provider_alias, provider_config in stack_config["azure"].items():
                # Credentials used to be at the same level as providers
                if provider_alias in ["credential", "credentials"]:
                    continue

                context_name = "" if provider_alias == "general" else provider_alias

                directory_id = provider_config.get("tenant_id", provider_config.get("directory_id", None))
                subscription_id = provider_config["subscription_id"]

                if not directory_id:
                    logger.error(
                        f'Please set the `azure.general.directory_id` variable in your "{provider_alias}" stack configuration.'
                    )
                    sys.exit(RC_KO)

                az_login_mode = provider_config.get("mode", "user")
                if az_login_mode.lower() == "user":
                    logger.info("Using Azure user mode")

                    try:
                        azure_tf_vars = azure.set_context(wrapper_config, subscription_id, directory_id, context_name)
                        terraform_vars.update(azure_tf_vars)
                    except azure.AzureError as e:
                        logger.error(f"Error while configuring Azure context: {e.message}")
                        sys.exit(RC_KO)

                elif az_login_mode.lower() in [
                    "sp",
                    "serviceprincipal",
                    "service_principal",
                ]:
                    logger.info("Using Azure Service Principal mode")

                    try:
                        profile = provider_config["credentials"]["profile"]
                    except KeyError:
                        try:
                            profile = stack_config["azure"]["credentials"]["profile"]
                        except KeyError:
                            # Backwards compatibility
                            profile = stack_config["azure"]["credential"]["profile"]
                    try:
                        azure_tf_vars = azure.set_context(wrapper_config, subscription_id, directory_id, context_name, profile)
                        terraform_vars.update(azure_tf_vars)
                    except azure.AzureError as e:
                        logger.error(f"Error while configuring Azure context: {e.message}")
                        sys.exit(RC_KO)
                else:
                    logger.error(
                        'Please use a correct Azure authentication mode ("user" or "service_principal") '
                        "in your stack YAML configuration."
                    )
                    sys.exit(RC_KO)

        set_terraform_vars(terraform_vars)
        os.environ["TF_PLUGIN_CACHE_DIR"] = wrapper_config["plugin_cache_dir"]

    # do we need a custom provider ?
    if args.subcommand in ["init", "bootstrap"]:
        for provider, config in stack_config.get("terraform", {}).get("custom-providers", {}).items():
            if type(config) == str:
                # This should be the version
                download_custom_provider(provider, config)
            else:
                # config should be a hash of version / extension
                download_custom_provider(provider, config["version"], config["extension"])

    # call subcommand
    returncode = args.func(wrapper_config)

    if returncode is not None:
        sys.exit(returncode)
    else:
        sys.exit(RC_OK)


if __name__ == "__main__":
    main()
