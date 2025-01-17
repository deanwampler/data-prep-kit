# Dean's "Friction Log" Notes - Pass 2

_June 6, 2024_

This is my second exploration of [`data-prep-lab`](https://github.com/IBM/data-prep-lab). This time, I decided to start with the contributor experience. Then I installed and ran through the getting-started content as a user of the tools, doing the first tutorial. Here is my "friction" log and recommendations.

Arguably, it was a mistake for me to start this way and not do the user examples first, because I spent a lot of time figuring out how to setup things. (I took this approach because I previously went through the example documentation.) Some of the steps I had to discover are covered in the examples. For example, the [Simplest Transform Tutorial](https://github.com/IBM/data-prep-kit/blob/dev/data-processing-lib/doc/simplest-transform-tutorial.md), which tells you to do the setup in the [ray/README](https://github.com/IBM/data-prep-kit/blob/dev/data-processing-lib/ray/README.md) first.

As now documented, the getting started process for end users is better than the first time I went through this, which is great! However, it is not yet the seductive _15-minutes to success_ experience that would be most desirable.

# TL;DR

I took detailed notes. Here are some highlights.

## TL;DR: Contributor Experience

See [Contributor Experience](#contributor-experience) for the detailed notes.

* I decided to start with the _contributor experience_, i.e., developing new features, etc. for DPK. This means setting up the environment to run the `make` processes, use an IDE, etc. 
  * This led me to a lot of tinkering to get things setup properly and working (more or less), as described below. 
  * The [CONTRIBUTING](https://github.com/IBM/data-prep-kit/blob/dev/CONTRIBUTING.md) guide really needs to be expanded to walk the developer through everything required to getting all `make` targets working, and ideally it should take minutes, not many hours. I muddled my way through, as you'll see, but I could have used one doc to walk me through all the details of setting up everything.
  * For example, I found myself running commands like `pip install data-processing-lib/python` manually. Would those have been automated somehow if I followed the "user path" first? 
* I had issues running `kind` with `podman` on an Intel Mac. I believe I got past them by leaning heavily on Podman Desktop and giving up on `make setup` when it couldn't create the `kind` cluster it wanted. However, I never got to the point of testing in `kind` (unless some tests did this for me...?), so I don't know if it really worked or not.
* It took many, many hours to get to the point where `make test` ran to completion. Contributors will need a lot of motivation and commitment.
* Support for Apple Silicon Macs is mandatory. Without it, most developers will not use this toolkit. This limitation will only get worse as existing Intel Mac developers upgrade.
* I saw some error messages scroll by during long builds, but the build didn't stop for them. I'm not sure if and when it should have stopped.
* I wasn't sure how to get the whole repo to load correct in VSCode so that all cross reference imports between modules "just worked". I'm not a Python expert, so I wasn't sure how how best to fix this. I stopped at this point, as I ran out of time for this evaluation effort.

## TL;DR: The Experience as a User of DPK APIs and Tools

See [The Experience as a User of DPK APIs and Tools](#the-experience-as-a-user-of-dpk-apis-and-tools) for the detailed notes.

This is the experience documented in the main [README](https://github.com/IBM/data-prep-lab), at least in the sense it gets you installed, then directs you to other docs for examples. 

* There are too many links you have to follow to do the first example. (I didn't go through any others.) I recommend one, extremely concise set of instructions to follow for each tutorial, including all additional setup required, so the user can get through each example in minutes, thereby finding the process seductive. This will also make it easier for the users to adapt the steps to their own applications.
* Consider creating a separate "template" repo, with all the examples a user might want to try out, then adapt to their needs. It should not require the main repo at all to work. 

## TL;DR: The Code

Having gone through this again, clearly a lot of effort has gone into the code, the `make` process, and the docs. The quality is high. It's a lot of work do this, I know, so please take the following in the spirit intended, to make a promising, potential OSS winner far more likely to succeed and justify the hard work. 

I strongly believe that trying to support Spark and "non-Ray python" execution have made the code more complicated than can be justified and should be reversed, focusing only on Ray. Here's why:

1. Spark is a declining ecosystem. I love Spark and I used it happily for years, but it is no longer growing. Without Databricks, it would probably be much more obscure these days than it is now. Supporting Spark should not be considered until we have evidence that customers doing data pipelines for AI want to use Spark for this purpose. Even then, you have to ask, what is unique that we bring over [Spark Datasets](https://spark.apache.org/docs/latest/sql-programming-guide.html) by themselves?
2. For single-node execution, Python without Ray makes little sense. Ray scales down well to single nodes. That's one of its powerful features, you can write the app _once_ with Ray, test it or even use in on a single machine (with full, robust multithreading), then redeploy on a cluster without code changes. Sure, there is more overhead running Ray on one node if you don't need clustering, but that leads to the next point.
3. Single-node execution is not a good target for DPK. If potential users really don't need a cluster, they are better off using Pandas, Dask, or similar mature, rich toolkits for data transformation and analysis. DPK won't appeal to them. It shines at large-scale data problems.
4. It is always better to keep a new system as simple as possible, grow adoption and experience using it, then evaluate expanding the features in ways that require more complicated architectures. Doing it the other way around, going broad at the beginning, is far more risky, as well as costly. Almost every enhancement will require three implementations or at least touching three subsystems. In contrast, the Ray-only DPK system worked well for DMF. Take that success into the public domain and drive larger adoption first, then let the community decide what breadth it wants to add. 

I know there were some "non-technical" considerations involved in the strategic decision to support Python-only and Spark execution. If you need permission from someone to remove the non-Ray options, I am willing to talk to whomever needs to hear the above points to explain why this is not the way to proceed, why it imperils the whole project.

# Detailed Friction Log

Here are the detailed notes.

## Contributor Experience

I forked the [`data-prep-lab`](https://github.com/IBM/data-prep-lab) repo (so I can do PRs...).

I set up a Conda environment with Python 3.11.9 and followed the [Getting Started](https://github.com/IBM/data-prep-kit/tree/dev?tab=readme-ov-file#-getting-started-) steps.

```shell
pip install pre-commit
pip install twine
...
git clone git@github.com:IBM/data-prep-kit.git
cd data-prep-kit
pre-commit install
```

Why is `dev` the default branch instead of the more conventional `main`?

I'll return to the rest of this section's instructions [later](#the-experience-as-a-user-of-dpk-apis-and-tools), which focus on users of the tools. Now, I'll pretend I am a contributor of new features, etc.

### Using `make`

I see there is a `make` process, so the first thing I did is this:

```shell
❯ make
Target               Description
------               -----------
build                Recursively build in all subdirs
clean                Recursively clean in all subdirs
lib-release          Publish data-prep-kit 0.2.0.dev6 and data-prep-kit-kfp 0.2.0.dev6 libraries to pypi
publish              Recursively publish in all subdirs
set-versions         Recursively set-versions in all subdirs
setup                Recursively setup in all subdirs
test                 Recursively test in all subdirs
```

Help is great! I was surprised how slow it was printing each line of the help.

It is more conventional for `make` to be equivalent to `make all`, which builds and tests everything, but a help target is great! Usually, In your case, I would expect `make all` to run `make clean setup test build`. (There isn't an `all` target currently, I'll provide a PR to add it, if you want it.) However, as you'll see, maybe running `setup` just has to be done separately, so maybe the instructions should be this:

```shell
# Run make setup one time:
❯ make setup
...
❯ make all # i.e., clean test build
```

> **Note:** FYI, I omitted the `publish` and related targets from `all` as they are also run occasionally, not "all the time"...

As a "make connoisseur", I appreciate the effort that went into this process and how well it is organized.

### `make setup`

Next I tried this:

```shell
❯ make clean setup  # adding clean first...
...
cd /Users/deanwampler/ibm/data-prep-kit/kind/hack/tools; ./kind_management.sh create_cluster dataprep
Installing kind cluster
kind could not be found. Please install it and try again
make[3]: *** [.create-kind-cluster] Error 1
make[2]: *** [setup] Error 2
make[1]: *** [.recurse] Error 2
make: *** [setup] Error 2
```

How do I install `kind`? Can it be installed by `setup` or if not, can it check if it's installed and tell me what to do, if not?

How about adding kind installation instructions in [Installation Steps](https://github.com/IBM/data-prep-kit/tree/dev?tab=readme-ov-file#installation-steps)? It looks like there is more to install in the [kind/README.md](https://github.com/IBM/data-prep-kit/tree/dev/kind), so maybe link to those instructions in [Installation Steps](https://github.com/IBM/data-prep-kit/tree/dev?tab=readme-ov-file#installation-steps)?

I eventually found my way to the [`kind` installation page](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) and installed it:

```shell
brew install kind
```

I also installed the Mac Intel `kubctl`:

```shell
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
```

Then I reran the `make` command:

```shell
❯ make clean setup
...
cd /Users/deanwampler/ibm/data-prep-kit/kind/hack/tools; ./kind_management.sh delete_cluster dataprep
Uninstalling kind cluster
Deleting cluster "dataprep" ...
ERROR: failed to delete cluster "dataprep": error listing nodes: failed to list nodes: command "docker ps -a --filter label=io.x-k8s.kind.cluster=dataprep --format '{{.Names}}'" failed with error: exit status 1
Command Output: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
make .create-kind-cluster
cd /Users/deanwampler/ibm/data-prep-kit/kind/hack/tools; ./kind_management.sh create_cluster dataprep
Installing kind cluster
ERROR: failed to create cluster: failed to list nodes: command "docker ps -a --filter label=io.x-k8s.kind.cluster=dataprep --format '{{.Names}}'" failed with error: exit status 1
Command Output: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
make[1]: *** [.create-kind-cluster] Error 1
make: *** [setup] Error 2
```

Ah, I need `docker`. I use `podman` (with `docker` aliased to it) so here goes:

```shell
❯ podman machine init
...
❯ podman machine start   # I've already initialized a machine.
Starting machine "podman-machine-default"
WARN[0000] podman helper is installed, but was not able to claim the global docker sock

This machine is currently configured in rootless mode. If your containers
require root permissions (e.g. ports < 1024), or if you run into compatibility
issues with non-podman clients, you can switch using the following command:

  podman machine set --rootful

API forwarding listening on: /var/folders/qj/y1tby9v55jl8dj3bz9tyxp8r0000gn/T/podman/podman-machine-default-api.sock

Another process was listening on the default Docker API socket address.
You can still connect Docker API clients by setting DOCKER_HOST using the
following command in your terminal session:

        export DOCKER_HOST='unix:///var/folders/qj/y1tby9v55jl8dj3bz9tyxp8r0000gn/T/podman/podman-machine-default-api.sock'

Machine "podman-machine-default" started successfully
```

Do I need to set `DOCKER_HOST` as described? Let's try without it first. I noticed the problems happened in the `kind` directory, so working there:

```shell
❯ cd kind
❯ make setup
make .create-kind-cluster
cd /Users/deanwampler/ibm/data-prep-kit/kind/hack/tools; ./kind_management.sh create_cluster dataprep
Installing kind cluster
ERROR: failed to create cluster: failed to list nodes: command "docker ps -a --filter label=io.x-k8s.kind.cluster=dataprep --format '{{.Names}}'" failed with error: exit status 1
Command Output: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
make[1]: *** [.create-kind-cluster] Error 1
make: *** [setup] Error 2
```

Curiously, if I run that `docker ps ...` command myself, it prints nothing and exits normally. Anyway, let's try setting `DOCKER_HOST`:

```shell
❯ export DOCKER_HOST='unix:///var/folders/qj/y1tby9v55jl8dj3bz9tyxp8r0000gn/T/podman/podman-machine-default-api.sock'
❯ make setup
make .create-kind-cluster
cd /Users/deanwampler/ibm/data-prep-kit/kind/hack/tools; ./kind_management.sh create_cluster dataprep
Installing kind cluster
ERROR: failed to create cluster: running kind with rootless provider requires setting systemd property "Delegate=yes", see https://kind.sigs.k8s.io/docs/user/rootless/
make[1]: *** [.create-kind-cluster] Error 1
make: *** [setup] Error 2
```

Obviously I'm setup to run rootless. The https://kind.sigs.k8s.io/docs/user/rootless/ page was not helpful, as it assumes a Linux system.

Instead, I used the [Podman Desktop](https://podman-desktop.io/) to start a `kind` cluster, which appeared to work :shrug:. We'll see...

Maybe not, I reran `make setup` to see if it would detect the kind cluster and be happy. It wasn't:

```shell
❯ export DOCKER_HOST='unix:///var/folders/qj/y1tby9v55jl8dj3bz9tyxp8r0000gn/T/podman/podman-machine-default-api.sock'
❯ make setup
make .create-kind-cluster
cd /Users/deanwampler/ibm/data-prep-kit/kind/hack/tools; ./kind_management.sh create_cluster dataprep
Installing kind cluster
ERROR: failed to create cluster: running kind with rootless provider requires setting systemd property "Delegate=yes", see https://kind.sigs.k8s.io/docs/user/rootless/
make[1]: *** [.create-kind-cluster] Error 1
make: *** [setup] Error 2
```

Let's assume it doesn't matter... What if we now return to the root directory and try `make build`? What's the worst that could happen?

### `make build`

```shell
❯ cd ..
❯ make build
(... long output suppressed ...)
```

I did see a lot of this:

```shell
...
creating src/UNKNOWN.egg-info
writing src/UNKNOWN.egg-info/PKG-INFO
writing dependency_links to src/UNKNOWN.egg-info/dependency_links.txt
...
```

What should `UNKNOWN` be?

Also, probably unique to my environment but annoying:

```shell
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
conda 24.1.0 requires packaging>=23.0, but you have packaging 21.3 which is incompatible.
```

Finally, after a long time (I forgot to time it), it finished with this error:

```shell
...
Successfully built unknown-0.0.0.tar.gz and UNKNOWN-0.0.0-py3-none-any.whl
make IMAGE_NAME_TO_VERIFY=data-prep-kit-spark-3.5.1 .defaults.verify-image-availability
Image data-prep-kit-spark-3.5.1 is not available locally.
make[9]: *** [.defaults.verify-image-availability] Error 1
make[8]: *** [.defaults.spark-lib-src-image] Error 2
make[7]: *** [.recurse] Error 2
make[6]: *** [build] Error 2
make[5]: *** [.recurse] Error 2
make[4]: *** [build] Error 2
make[3]: *** [.recurse] Error 2
make[2]: *** [build] Error 2
make[1]: *** [.recurse] Error 2
make: *** [build] Error 2
```

What was supposed to build the `data-prep-kit-spark-3.5.1` image? Maybe I missed it, so I decided to run it again, time it, and capture all the log output for examination:

```shell
❯ time make build > build.log 2>&1
make build > build.log 2>&1  42.92s user 17.12s system 74% cpu 1:20.65 total
```

Still missing

```shell
...
make IMAGE_NAME_TO_VERIFY=data-prep-kit-spark-3.5.1 .defaults.verify-image-availability
Image data-prep-kit-spark-3.5.1 is not available locally.
...
```

Looking through the various make files, it looks like the Spark build wasn't done, but the process still checked for the image. True?

Here's what Images I have:

```shell
❯ podman images
REPOSITORY                                           TAG          IMAGE ID      CREATED         SIZE
quay.io/dataprep1/data-prep-kit/doc_id-ray           0.4.0.dev6   74698b453f28  4 minutes ago   2.38 GB
docker.io/library/doc_id-ray                         0.4.0.dev6   74698b453f28  4 minutes ago   2.38 GB
quay.io/dataprep1/data-prep-kit/proglang_select-ray  0.4.0.dev6   35f40e2b8be5  4 minutes ago   2.38 GB
docker.io/library/proglang_select-ray                0.4.0.dev6   35f40e2b8be5  4 minutes ago   2.38 GB
quay.io/dataprep1/data-prep-kit/malware-ray          0.5.0.dev6   8c8552600862  24 minutes ago  2.79 GB
docker.io/library/malware-ray                        0.5.0.dev6   8c8552600862  24 minutes ago  2.79 GB
<none>                                               <none>       4ea1daee1f3a  25 minutes ago  2.85 GB
quay.io/dataprep1/data-prep-kit/code_quality-ray     0.4.0.dev6   19dbeb3d2669  26 minutes ago  2.47 GB
docker.io/library/code_quality-ray                   0.4.0.dev6   19dbeb3d2669  26 minutes ago  2.47 GB
docker.io/clamav/clamav                              latest       62739950020f  3 days ago      314 MB
docker.io/kindest/node                               <none>       9319cf209ac5  3 weeks ago     980 MB
docker.io/rayproject/ray                             2.9.3-py310  ef9684d6c5bf  3 months ago    2.2 GB
```

Not sure how to proceed, but can I run `make test`?

### `make test`

[CONTRIBUTING](https://github.com/IBM/data-prep-kit/blob/dev/CONTRIBUTING.md) this line near the end:

> Makefiles are use for most of the automation and you should be able to use `make test` in most directories.

Unfortunately, developers will be frustrated if they can't type `make test` at the root directory and have it work easily for all sub-directories. How will they know which ones they can "ignore"?

If you don't want to make this seamless out of the box, at least document the minimum paths through the system depending on user interest. E.g., what can I suppress or ignore if I don't care about Spark?

```shell
❯ make -w test  # -w to print directories Make enters.
make: Entering directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler'
make[1]: Entering directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler'
SUB_MAKE_DIRS= data-processing-lib transforms kfp kind
Using recursive test rule in data-processing-lib
make[2]: Entering directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib'
make[3]: Entering directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib'
SUB_MAKE_DIRS=dist/ doc/ play/ python/ ray/ spark/ src/ test/ venv/
No Makefile found in dist/. Skipping.
No Makefile found in doc/. Skipping.
No Makefile found in play/. Skipping.
Using recursive test rule in python/
make[4]: Entering directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/python'
source venv/bin/activate; export PYTHONPATH=../src; cd test; pytest -s  data_processing_tests/data_access;
/bin/bash: venv/bin/activate: No such file or directory
=================================================================== test session starts ====================================================================
platform darwin -- Python 3.8.18, pytest-7.1.2, pluggy-1.0.0
rootdir: /Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/python, configfile: pyproject.toml
plugins: mock-3.10.0, hypothesis-6.47.3, cov-3.0.0
collected 0 items / 4 errors

========================================================================== ERRORS ==========================================================================
________________________________________ ERROR collecting test/data_processing_tests/data_access/daf_local_test.py _________________________________________
ImportError while importing test module '/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/python/test/data_processing_tests/data_access/daf_local_test.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/Cellar/python@3.8/3.8.18_1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/importlib/__init__.py:127: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
data_processing_tests/data_access/daf_local_test.py:3: in <module>
    from data_processing.test_support.data_access import AbstractDataAccessFactoryTests
../src/data_processing/test_support/__init__.py:1: in <module>
    from .abstract_test import AbstractTest, get_tables_in_folder
../src/data_processing/test_support/abstract_test.py:18: in <module>
    import pyarrow as pa
E   ModuleNotFoundError: No module named 'pyarrow'
____________________________________ ERROR collecting test/data_processing_tests/data_access/data_access_local_test.py _____________________________________
ImportError while importing test module '/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/python/test/data_processing_tests/data_access/data_access_local_test.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/Cellar/python@3.8/3.8.18_1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/importlib/__init__.py:127: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
data_processing_tests/data_access/data_access_local_test.py:19: in <module>
    import pyarrow
E   ModuleNotFoundError: No module named 'pyarrow'
______________________________________ ERROR collecting test/data_processing_tests/data_access/data_access_s3_test.py ______________________________________
ImportError while importing test module '/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/python/test/data_processing_tests/data_access/data_access_s3_test.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/Cellar/python@3.8/3.8.18_1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/importlib/__init__.py:127: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
data_processing_tests/data_access/data_access_s3_test.py:15: in <module>
    from data_processing.data_access import DataAccessS3
../src/data_processing/data_access/__init__.py:1: in <module>
    from data_processing.data_access.arrow_s3 import ArrowS3
../src/data_processing/data_access/arrow_s3.py:16: in <module>
    import pyarrow as pa
E   ModuleNotFoundError: No module named 'pyarrow'
____________________________________ ERROR collecting test/data_processing_tests/data_access/sample_input_data_test.py _____________________________________
ImportError while importing test module '/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/python/test/data_processing_tests/data_access/sample_input_data_test.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/Cellar/python@3.8/3.8.18_1/Frameworks/Python.framework/Versions/3.8/lib/python3.8/importlib/__init__.py:127: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
data_processing_tests/data_access/sample_input_data_test.py:15: in <module>
    from data_processing.data_access import DataAccessLocal
../src/data_processing/data_access/__init__.py:1: in <module>
    from data_processing.data_access.arrow_s3 import ArrowS3
../src/data_processing/data_access/arrow_s3.py:16: in <module>
    import pyarrow as pa
E   ModuleNotFoundError: No module named 'pyarrow'
================================================================= short test summary info ==================================================================
ERROR data_processing_tests/data_access/daf_local_test.py
ERROR data_processing_tests/data_access/data_access_local_test.py
ERROR data_processing_tests/data_access/data_access_s3_test.py
ERROR data_processing_tests/data_access/sample_input_data_test.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
==================================================================== 4 errors in 0.53s =====================================================================
make[4]: *** [test] Error 2
make[4]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/python'
make[3]: *** [.recurse] Error 2
make[3]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib'
make[2]: *** [test] Error 2
make[2]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib'
make[1]: *** [.recurse] Error 2
make[1]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler'
make: *** [test] Error 2
make: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler'
```

Missing `pyarrow` dependency? I notice there is a `data-processing-lib/python/pyproject.toml` file. Maybe a README somewhere says to install it, but I don't know where...

```shell
❯ pip install data-processing-lib/python/
...
Successfully installed argparse-1.4.0 boto3-1.34.69 data_prep_toolkit-0.2.0.dev6 mmh3-4.1.0 pyarrow-15.0.2
❯ make -w test
...
E   ModuleNotFoundError: No module named 'moto'
...
❯ pip install moto  # I'll do a PR to add moto to the pyproject.toml file.
...
❯ make -w test

```

I saw some error messages scroll by during `make -w test`, but the build didn't stop for them, until it hit the missing `ray` library in `/Users/deanwampler/ibm/data-prep-kit/data-processing-lib/ray`. Not sure if and when it should have stopped sooner. Other errors involved `venv` environments. Here's the same output filtered for `error`, ignoring case:

```shell
❯ make -w test 2>&1 | grep -i error
....20:33:52 ERROR - Error reading table from non_existent_file.parquet:
.20:33:52 ERROR - Error reading table from invalid_file.txt:
.20:33:52 ERROR - Error reading table from malformed_parquet.parquet:
....20:33:52 ERROR - Error saving table to /tmp/output.parquet: Write error
....20:33:52 ERROR - Error reading file nonexistent_file.txt: [Errno 2] No such file or directory: 'nonexistent_file.txt'
.20:33:52 ERROR - Error reading file invalid_gz.gz: Not a gzipped file (b'In')
........20:33:52 ERROR - Error saving bytes to file : [Errno 2] No such file or directory: ''
20:33:56 ERROR - data access factory data_: missing s3_credentials
20:33:56 ERROR - data factory data_ S3, Local configurations specified, but only one configuration expected
20:33:56 ERROR - data access factory data_: Could not find input folder in local config
20:33:56 ERROR - data access factory data_: Could not find output folder in local config
20:33:56 ERROR - data access factory data_: Could not find input folder in local config
20:33:56 ERROR - data access factory data_: Could not find output folder in local config
20:33:56 ERROR - data access factory data_: Could not find input folder in s3 config
20:33:56 ERROR - data access factory data_: Could not find output folder in s3 config
20:33:56 ERROR - data access factory data_: Could not find input folder in s3 config
20:33:56 ERROR - data access factory data_: Could not find output folder in s3 config
collected 0 items / 1 error
==================================== ERRORS ====================================
_ ERROR collecting test/data_processing_ray_tests/launch/ray/ray_util_test.py __
ImportError while importing test module '/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/ray/test/data_processing_ray_tests/launch/ray/ray_util_test.py'.
E   ModuleNotFoundError: No module named 'ray'
ERROR data_processing_ray_tests/launch/ray/ray_util_test.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.24s ===============================
make[4]: *** [test] Error 2
make[3]: *** [.recurse] Error 2
make[2]: *** [test] Error 2
make[1]: *** [.recurse] Error 2
make: *** [test] Error 2
```

To fix the missing Ray dependency:

```shell
❯ pip install data-processing-lib/ray
...
Installing collected packages: wcwidth, py-spy, opencensus-context, nvidia-ml-py, colorful, argparse, wrapt, websockets, uvloop, ujson, typing-extensions, sniffio, shellingham, rpds-py, python-multipart, python-dotenv, pyasn1, psutil, protobuf, prometheus-client, pillow, orjson, multidict, msgpack, httptools, h11, grpcio, frozenlist, dnspython, click, cachetools, blessed, attrs, annotated-types, yarl, uvicorn, smart-open, rsa, referencing, pydantic-core, pyasn1-modules, proto-plus, httpcore, gpustat, googleapis-common-protos, email_validator, anyio, aiosignal, watchfiles, typer, starlette, pydantic, jsonschema-specifications, httpx, google-auth, aiohttp, jsonschema, google-api-core, fastapi-cli, aiohttp-cors, ray, opencensus, fastapi, data_prep_toolkit_ray
Successfully installed aiohttp-3.9.5 aiohttp-cors-0.7.0 aiosignal-1.3.1 annotated-types-0.7.0 anyio-4.4.0 argparse-1.4.0 attrs-23.2.0 blessed-1.20.0 cachetools-5.3.3 click-8.1.7 colorful-0.5.6 data_prep_toolkit_ray-0.2.0.dev6 dnspython-2.6.1 email_validator-2.1.1 fastapi-0.111.0 fastapi-cli-0.0.4 frozenlist-1.4.1 google-api-core-2.19.0 google-auth-2.30.0 googleapis-common-protos-1.63.1 gpustat-1.1.1 grpcio-1.64.1 h11-0.14.0 httpcore-1.0.5 httptools-0.6.1 httpx-0.27.0 jsonschema-4.22.0 jsonschema-specifications-2023.12.1 msgpack-1.0.8 multidict-6.0.5 nvidia-ml-py-12.555.43 opencensus-0.11.4 opencensus-context-0.1.3 orjson-3.10.3 pillow-10.3.0 prometheus-client-0.20.0 proto-plus-1.23.0 protobuf-4.25.3 psutil-5.9.8 py-spy-0.3.14 pyasn1-0.6.0 pyasn1-modules-0.4.0 pydantic-2.7.3 pydantic-core-2.18.4 python-dotenv-1.0.1 python-multipart-0.0.9 ray-2.9.3 referencing-0.35.1 rpds-py-0.18.1 rsa-4.9 shellingham-1.5.4 smart-open-7.0.4 sniffio-1.3.1 starlette-0.37.2 typer-0.12.3 typing-extensions-4.12.1 ujson-5.10.0 uvicorn-0.30.1 uvloop-0.19.0 watchfiles-0.22.0 wcwidth-0.2.13 websockets-12.0 wrapt-1.16.0 yarl-1.9.4
```

> Q: Shouldn't these `pip install data-processing-lib/...` commands be executed by `make setup`?

Now Spark is missing:

```shell
❯ make -w test
...
============================================================================================= ERRORS ==============================================================================================
_______________________________________________________ ERROR collecting test/data_processing_spark_tests/launch/spark/test_noop_launch.py ________________________________________________________
ImportError while importing test module '/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/spark/test/data_processing_spark_tests/launch/spark/test_noop_launch.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
data_processing_spark_tests/launch/spark/test_noop_launch.py:15: in <module>
    from data_processing_spark.runtime.spark.spark_launcher import SparkTransformLauncher
../src/data_processing_spark/runtime/spark/__init__.py:12: in <module>
    from data_processing_spark.runtime.spark.runtime_config import SparkTransformRuntimeConfiguration
../src/data_processing_spark/runtime/spark/runtime_config.py:13: in <module>
    from data_processing_spark.runtime.spark.spark_transform import AbstractSparkTransform
../src/data_processing_spark/runtime/spark/spark_transform.py:16: in <module>
    from pyspark.sql import DataFrame
E   ModuleNotFoundError: No module named 'pyspark'
===================================================================================== short test summary info =====================================================================================
ERROR data_processing_spark_tests/launch/spark/test_noop_launch.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
======================================================================================== 1 error in 0.40s =========================================================================================
make[4]: *** [test] Error 2
make[4]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/spark'
make[3]: *** [.recurse] Error 2
make[3]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib'
make[2]: *** [test] Error 2
make[2]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib'
make[1]: *** [.recurse] Error 2
make[1]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler'
make: *** [test] Error 2
make: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler'
```

Once again:

```shell
❯ pip install data-processing-lib/spark
... success ...
❯ make -w test
... failure of Ray tests for missing bs4 ... 
❯ pip install bs4
...
❯ make -w test
... failure of Ray tests for missing transformers ... 
❯ pip install transformers
...
```

I will do another PR to add `bs4` and `transformers` to `.../ray/pyproject.toml`.

I thought I got through the Ray tests before when I hit the Spark error, but maybe I overlooked something...


```shell
❯ make -w test
...
============================================================================================= ERRORS ==============================================================================================
___________________________________________________________________________ ERROR collecting test/test_code_quality.py ____________________________________________________________________________
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/utils/_errors.py:304: in hf_raise_for_status
    response.raise_for_status()
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/requests/models.py:1021: in raise_for_status
    raise HTTPError(http_error_msg, response=self)
E   requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: https://huggingface.co/codeparrot/codeparrot/resolve/main/tokenizer_config.json

The above exception was the direct cause of the following exception:
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/transformers/utils/hub.py:399: in cached_file
    resolved_file = hf_hub_download(
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/utils/_validators.py:114: in _inner_fn
    return fn(*args, **kwargs)
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/file_download.py:1221: in hf_hub_download
    return _hf_hub_download_to_cache_dir(
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/file_download.py:1325: in _hf_hub_download_to_cache_dir
    _raise_on_head_call_error(head_call_error, force_download, local_files_only)
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/file_download.py:1823: in _raise_on_head_call_error
    raise head_call_error
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/file_download.py:1722: in _get_metadata_or_catch_error
    metadata = get_hf_file_metadata(url=url, proxies=proxies, timeout=etag_timeout, headers=headers)
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/utils/_validators.py:114: in _inner_fn
    return fn(*args, **kwargs)
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/file_download.py:1645: in get_hf_file_metadata
    r = _request_wrapper(
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/file_download.py:372: in _request_wrapper
    response = _request_wrapper(
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/file_download.py:396: in _request_wrapper
    hf_raise_for_status(response)
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/huggingface_hub/utils/_errors.py:352: in hf_raise_for_status
    raise RepositoryNotFoundError(message, response) from e
E   huggingface_hub.utils._errors.RepositoryNotFoundError: 401 Client Error. (Request ID: Root=1-666267d3-334983361564bf8029a6c54c;1daa1f66-1e18-40b6-a37e-54213b12f847)
E
E   Repository Not Found for url: https://huggingface.co/codeparrot/codeparrot/resolve/main/tokenizer_config.json.
E   Please make sure you specified the correct `repo_id` and `repo_type`.
E   If you are trying to access a private or gated repo, make sure you are authenticated.
E   Organization API tokens are deprecated and have stopped working. Use User Access Tokens instead: https://huggingface.co/settings/tokens

The above exception was the direct cause of the following exception:
test_code_quality.py:41: in get_test_transform_fixtures
    CodeQualityTransform(config),
../src/code_quality_transform_ray.py:205: in __init__
    self.tokenizer = AutoTokenizer.from_pretrained(
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/transformers/models/auto/tokenization_auto.py:817: in from_pretrained
    tokenizer_config = get_tokenizer_config(pretrained_model_name_or_path, **kwargs)
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/transformers/models/auto/tokenization_auto.py:649: in get_tokenizer_config
    resolved_config_file = cached_file(
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/site-packages/transformers/utils/hub.py:422: in cached_file
    raise EnvironmentError(
E   OSError: codeparrot/codeparrot is not a local folder and is not a valid model identifier listed on 'https://huggingface.co/models'
E   If this is a private repository, make sure to pass a token having permission to this repo either by logging in with `huggingface-cli login` or by passing `token=<your_token>`
===================================================================================== short test summary info =====================================================================================
ERROR test_code_quality.py::TestCodeQualityTransform - OSError: codeparrot/codeparrot is not a local folder and is not a valid model identifier listed on 'https://huggingface.co/models'
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
======================================================================================== 1 error in 1.74s =========================================================================================
make[8]: *** [.defaults.test-src] Error 2
make[8]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/transforms/code/code_quality/ray'
make[7]: *** [.recurse] Error 2
make[7]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/transforms/code/code_quality'
make[6]: *** [test] Error 2
make[6]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/transforms/code/code_quality'
make[5]: *** [.recurse] Error 2
make[5]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/transforms/code'
make[4]: *** [test] Error 2
make[4]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/transforms/code'
make[3]: *** [.recurse] Error 2
make[3]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/transforms'
make[2]: *** [test] Error 2
make[2]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/transforms'
make[1]: *** [.recurse] Error 2
make[1]: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler'
make: *** [test] Error 2
make: Leaving directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler'
```

Alas, dependencies seem to be fixed, but now tests are failing.
It could be I need Hugging Face credentials. There are comments buried in a few READMEs about HF tokens, etc. Was this described in a top-level README that I missed?

Incidentally, after realizing I needed to run commands like `pip install data-processing-lib/spark`, I decided to try the top-level `make build` again and see if the Spark stuff would now build successfully. I got the same error:

```
...
Successfully built unknown-0.0.0.tar.gz and UNKNOWN-0.0.0-py3-none-any.whl
make IMAGE_NAME_TO_VERIFY=data-prep-kit-spark-3.5.1 .defaults.verify-image-availability
make[9]: Entering directory `/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/transforms/universal/doc_id/spark'
Image data-prep-kit-spark-3.5.1 is not available locally.
make[9]: *** [.defaults.verify-image-availability] Error 1
...
```

# Comments on the Project Structure and Code

## Dependencies Between Modules

I noticed lines like this in `data-processing-lib/ray/pyproject.toml`:

```
    "data-prep-toolkit==0.2.0.dev6",
```

Can't `data-prep-toolkit` be handled as a relative path dependency in import statements or do you intend to bundle separate archives with dependencies between them? Also, the hard-coded version makes me nervous. Do you have a way to keep these versions in sync and up to date?

I'm not _really_ a Python expert, but when I opened the whole repo in VSCode, it couldn't resolve imports in the `ray` files that were implemented elsewhere in the repo. What should the user do to make VSCode, PyCharm, etc. work out of the box?

## `pyproject.toml` Files

There are 9 non-empty `pyproject.toml` files and 5 that are empty. Why so many? Why the empty ones? I explicit ran `pip install ...` on several of them, as described above. Which ones should the developer use?

Many are clearly similar. Can they be cut down to just one or worst case three, one for Ray, Spark, and "bare" Python?

Also, is it possible to support `pip install data-prep-kit[ray]`, etc. for installing the "optional" packages? 

This is all I decided to do for now on the _contributor experience_. Let's switch to just using DPK as described in the main [README](https://github.com/IBM/data-prep-kit).

## The Experience as a User of DPK APIs and Tools

I did the [Installation Steps](https://github.com/IBM/data-prep-kit?tab=readme-ov-file#installation-steps) above. However, I would really expect the following steps:

```shell
...
git clone git@github.com:IBM/data-prep-kit.git
cd data-prep-kit
pre-commit install
```

to be replaced by `pip install ...`:

```shell
pip install data-prep-kit[ray]  # Also install Ray support.
```

I assume this is planned... Organizations that control their dependencies carefully will be reluctant to run production software that is installed by `git clone` commands.

Now let's try the examples.

### Build Your Own Transforms

This section says:

> Follow the documentation [here](https://github.com/IBM/data-prep-kit/blob/dev/data-processing-lib/doc/overview.md) to build your own transform.

But that documentation doesn't take you to a tutorial that gets you started quickly. It takes you to a tree of very good docs about the API involved, but you feel lost quickly until you noticed the [Transform Examples](https://github.com/IBM/data-prep-kit/blob/dev/data-processing-lib/doc/transform-tutorial-examples.md) link. Now you have a few tutorials.

> Put the link to this page in the top-level README, then relabel the existing link to `Transform documentation` or something like that.

I tried the [Simplest Transform Tutorial](https://github.com/IBM/data-prep-kit/blob/dev/data-processing-lib/doc/simplest-transform-tutorial.md).

It tells me to do the setup instructions in [ray/README](https://github.com/IBM/data-prep-kit/blob/dev/data-processing-lib/ray/README.md):

```shell
❯ cd data-processing-lib/ray
❯ make venv
make .defaults.ray-lib-src-venv
python -m venv venv
...
WARNING: Skipping data-prep-toolkit as it is not installed.
WARNING: Skipping data-prep-toolkit-ray as it is not installed.
Installing Ray and Python data processing library source to existing venv
Obtaining file:///Users/deanwampler/ibm/data-prep-kit/data-processing-lib/python
...
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
data-prep-toolkit 0.2.0.dev6 requires moto==5.0.9, but you have moto 5.0.5 which is incompatible.
Successfully installed markupsafe-2.0.1 moto-5.0.5 werkzeug-2.1.2
```

Do those errors matter about `data-prep-kit`??

If forced `pip` to install v5.0.9, `❯ pip install moto==5.0.9`.

```shell
❯ source venv/bin/activate
❯ make test build
source venv/bin/activate; export PYTHONPATH=../src; cd test; pytest -s  data_processing_ray_tests/launch/ray/ray_util_test.py;
======================================================================================= test session starts =======================================================================================
platform darwin -- Python 3.11.9, pytest-8.2.2, pluggy-1.5.0
rootdir: /Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/ray
configfile: pyproject.toml
plugins: anyio-4.4.0
collected 0 items / 1 error

============================================================================================= ERRORS ==============================================================================================
___________________________________________________________ ERROR collecting test/data_processing_ray_tests/launch/ray/ray_util_test.py ___________________________________________________________
ImportError while importing test module '/Users/deanwampler/ibm/data-prep-kit/data-prep-kit-deanwampler/data-processing-lib/ray/test/data_processing_ray_tests/launch/ray/ray_util_test.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/Caskroom/miniforge/base/envs/data-prep-kit/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
data_processing_ray_tests/launch/ray/ray_util_test.py:15: in <module>
    from data_processing.utils import GB, TransformUtils
E   ModuleNotFoundError: No module named 'data_processing'
===================================================================================== short test summary info =====================================================================================
ERROR data_processing_ray_tests/launch/ray/ray_util_test.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
======================================================================================== 1 error in 0.77s =========================================================================================
make: *** [test] Error 2
```

> **Note:** I did not include the `publish` target shown in the README, because I assume you don't want me pushing an update to PyPi!

Yes, the `data-prep-kit` errors **did** mattered during `make venv`.

There is a `pyproject.toml` file in this directory. Hmm...

```shell
❯ pip install .
...
Successfully built data_prep_toolkit_ray
Installing collected packages: argparse, data-prep-toolkit, data_prep_toolkit_ray
Successfully installed argparse-1.4.0 data-prep-toolkit-0.2.0.dev6 data_prep_toolkit_ray-0.2.0.dev6
```

Why the inconsistent case? `data-prep-toolkit-0.2.0.dev6` vs. `data_prep_toolkit_ray-0.2.0.dev6`.

Is the `0.2.0.dev6` version up to date with this git repo I'm working in?

Trying `make` again:


```shell
❯ make test build
... success ...
```

Now back to the [tutorial](https://github.com/IBM/data-prep-kit/blob/dev/data-processing-lib/doc/simplest-transform-tutorial.md).

I see it tells me I can find the example code in the [noop transform](https://github.com/IBM/data-prep-kit/tree/dev/transforms/universal/noop) dir, but really it looks like I want to navigate into the [ray subdirectory](https://github.com/IBM/data-prep-kit/tree/dev/transforms/universal/noop/ray).

Let's try the `make` commands listed in the README:

```shell
❯ make run-cli-sample
make RUN_FILE=noop_transform_ray.py \
    RUN_ARGS="--run_locally True --data_local_config \"{ 'input_folder' : '../test-data/input', 'output_folder' : '../output'}\" " .transforms.run-src-file

Please 'make venv' before running noop_transform_ray.py.

make[1]: *** [.defaults.run-src-file] Error 1
make: *** [.transforms.run-cli-ray-sample] Error 2
```

Why not have `venv` as a dependency of `run-cli-sample`?? Okay, it takes a while to go through `venv` for every target. At least tell me in the README to do this first, e.g., in the list of example commands.

```shell
❯ make venv
...
❯ make run-cli-sample
...
13:06:41 INFO - Completed execution in 0.3045286814371745 min, execution result 0
❯ make run-local-sample
...
13:09:26 INFO - Completed execution in 0.30522746642430626 min, execution result 0
❯ ll output
Permissions  Size User        Group Date Modified Name
.rw-r--r--  1.3Ki deanwampler staff  8 Jun 13:09  metadata.json
.rw-r--r--    753 deanwampler staff  8 Jun 13:09  test1.parquet
```

I skipped the S3 sample.

That's all I have time to work on this. In general, this one tutorial worked, but it took time to navigate the different README files and do the setup steps. I'm a bit lost at this point; it would take some effort to reproduce these steps in a standalone application of my own. 

Consider creating a completely separate `examples` directory tree with the bare minimum connections to the main source code trees. 

Even better, create a separate "template" repo, with all the examples a user might want to try out, then adapt to their needs. It should not require the main repo at all to work.


