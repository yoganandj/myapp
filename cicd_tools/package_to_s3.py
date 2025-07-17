import os
import sys
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory
from configparser import ConfigParser
from typing import List, Optional, Iterator, Tuple
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path

import boto3

ARTIFACTS_BUCKET = "myapp-digital-artifacts"
S3_CLIENT = boto3.client('s3')
IGNORED_ELEMENTS = ['__pycache__',]

class ObjectType(Enum):
    LAMBDA = "lambda"
    LAYER = "layer"

@dataclass
class ObjectConfig:
    type: ObjectType
    stack_name: str
    dir_path: Optional[Path]
    name: str
    filters: str
    include: Optional[str]
    no_deps: bool
    use_setup_py: bool
    wheel_specific_for_lambda_with_python: Optional[float]

    @property
    def entries(self) -> List[Path]:
        entries = []
        for filter_ in self.filters.split(','):
            entries.extend(self.dir_path.rglob(filter_.strip()))
        return list({e for e in entries if "__pycache__" not in str(e) and not is_hidden_file(e)})

    @property
    def included_entries(self) -> Iterator[Tuple[Path, List[Path]]]:
        for dir_ in (Path(x) for x in self.include.split(',') if Path(x).is_dir()):
            files = list({f for f in dir_.rglob('*') if "__pycache__" not in str(f) and not is_hidden_file(f)})
            yield dir_, files


def is_hidden_file(entry):
    return any((e for e in entry.parts if e.startswith('.')))

def upload_to_s3(zip_path: Path, remote_zip_key: str) -> None:
    try:
        S3_CLIENT.upload_file(str(zip_path), ARTIFACTS_BUCKET, remote_zip_key, ExtraArgs={'ACL': 'bucket-owner-full-control'})
        print(f"Uploaded {zip_path} to s3://{ARTIFACTS_BUCKET}/{remote_zip_key}")
    except Exception as e:
        print(f"Failed to upload {zip_path} to S3: {e}")
        sys.exit(1)

def embed_requirements_dependencies_into_zipfile(object_config: ObjectConfig, zipfile: ZipFile, requirements_path: Path) -> None:
    sup_args = ["-r", str(requirements_path)]
    embed_dependencies_into_zipfile(object_config, zipfile, sup_args)

def embed_setup_py_dependencies_into_zipfile(object_config: ObjectConfig, zipfile: ZipFile) -> None:
    sup_args = ["-e", "."]
    embed_dependencies_into_zipfile(object_config, zipfile, sup_args)    

def embed_dependencies_into_zipfile(object_config: ObjectConfig, zipfile: ZipFile, sup_args: List[str]) -> None:
    with TemporaryDirectory() as object_dependencies_dir:
        object_dependencies_path = Path(object_dependencies_dir)
        if object_config.type == ObjectType.LAYER:
            object_dependencies_path = object_dependencies_path / "python"
        args = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--root-user-action=ignore",
            "--upgrade",
            "-q",
            "-t", str(object_dependencies_path),
        ] + sup_args   

        if object_config.no_deps:
            args.insert(5, "--no-deps")
        if object_config.wheel_specific_for_lambda_with_python:
            args.insert(5, f"--python-version={object_config.wheel_specific_for_lambda_with_python}")
            args.insert(5,"--only-binary=:all:")
            args.insert(5,"--platform=manylinux2014_x86_64")
            args.insert(5,"--implementation=cp")

        subprocess.check_call(args)

        for entry in Path(object_dependencies_path).rglob('*'):
            if not any(e in str(entry) for e in IGNORED_ELEMENTS):
                zipfile.write(entry, entry.relative_to(object_dependencies_path))

def zip_object(temporary_file: NamedTemporaryFile, object_config: ObjectConfig) -> None:
    with ZipFile(temporary_file, 'w', ZIP_DEFLATED) as zipfile:
        if object_config.dir_path:
            for entry in object_config.entries:
                entry_relative_to = entry.relative_to(object_config.dir_path)
                entry_relative_to = (
                    Path("python", entry_relative_to) if object_config.type == ObjectType.LAYER else entry_relative_to
                )
                zipfile.write(entry, entry_relative_to)
            requirements_path = Path(object_config.dir_path, "requirements.txt")
            if requirements_path.exists():
                embed_requirements_dependencies_into_zipfile(object_config, zipfile, requirements_path)

        if object_config.include:
            for included_dir, included_files in object_config.included_entries:
                zipfile.write(included_dir, included_dir.name)
                for entry in included_files:
                    zipfile.write(entry, entry.relative_to(included_dir.parent))

        if object_config.use_setup_py:
            embed_setup_py_dependencies_into_zipfile(object_config, zipfile)

        if not zipfile.filelist:
            raise Exception(f"Zip file for {object_config.name} is empty. Or requirements.txt was found.")         


def package_object(object_config: ObjectConfig) -> None:
    remote_zip_key = "/".join(
        (
            os.environ["ENV"], # Eg: dev02
            object_config.type.value, # Eg: data_impact_ingestion
            object_config.stack_name, # Eg: lambda
            f"{object_config.name}.zip" # carbon_replay_glue_job_invoke.zip
        )
    )
    with NamedTemporaryFile() as fp:
        zip_object(fp, object_config)
        upload_to_s3(fp.name, remote_zip_key)
    print(
        f"{object_config.type.value.capitalize()} {object_config.name} has been successfully deployed: to s3://{ARTIFACTS_BUCKET}/{remote_zip_key}",
        flush=True,
    )      
    print(f"Python version: {sys.version}", flush=True)

def parse_config() -> ConfigParser:
    config = ConfigParser()
    config.read('s3_deployments.cfg')
    if "metadata" not in config:
        print("Configuration file 's3_deployments.cfg' is missing the 'metadata' section.")
        raise Exception("Configuration file must contain a metadata seciton")
    return config

def get_config(config: ConfigParser) -> Iterator[ObjectConfig]:
    configs = (config[s] for s in config.sections() if s.startswith("deploy."))
    for object_config in configs:
        yield ObjectConfig(
            type=ObjectType(object_config.get("type")),
            stack_name=config["metadata"]["stack_name"].strip(),
            dir_path=Path(object_config["path"].strip()) if "path" in object_config else None,
            name=object_config.name.split(".")[-1],
            filters=object_config.get("filters", "*"),
            include=object_config.get("include", None),
            no_deps=object_config.getboolean("no_deps", "").lower() == "true"   ,
            use_setup_py=object_config.get("use_setup_py", "").lower() == "true",
            wheel_specific_for_lambda_with_python=object_config.get("wheel_specific_for_lambda_with_python", None),
        )

def main() -> None:
    config = parse_config()

    object_configs = list(get_config(config))
    print("Found objects :",", ".join(oc.name for oc in object_configs))

    should_exit_with_error = False
    with ThreadPoolExecutor(max_workers=len(object_configs)) as executor:
        futures = {executor.submit(package_object, oc): oc for oc in object_configs}
        for future in as_completed(futures):
            if future.exception() is not None:
                print(
                    f"Could not deploy {futures[future].type.value} "
                    f"{futures[future].name}: {repr(future.exception())}"
                )        
                should_exit_with_error = True

    if should_exit_with_error:
        print("Something wrong happened for at least one of the packageings")
        sys.exit(1)

if __name__ == "__main__":
    main()
