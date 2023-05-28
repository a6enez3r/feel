FROM python:latest AS compile-image

# Add src
ADD feel /root/feel/feel
ADD requirements /root/feel/requirements
ADD README.md /root/feel/README.md
ADD setup.py /root/feel/setup.py
ADD setup.cfg /root/feel/setup.cfg
ADD versioneer.py /root/feel/versioneer.py

# Init gh
RUN apt update

# Install
RUN pip install /root/feel

ENTRYPOINT [ "feel" ]

# FROM python:3.10-slim AS build-image
# COPY --from=compile-image /root/.local /root/.local

# # Authentication: specify GH_TOKEN in the environment

# # Make sure scripts in .local are usable:
# ENV PATH=/root/.local/bin:$PATH
# # Run on startup
# ENTRYPOINT [ "feel" ]