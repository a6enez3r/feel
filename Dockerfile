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
