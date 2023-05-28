FROM python:latest

# Add src
ADD feel /root/feel/feel
ADD requirements /root/feel/requirements
ADD README.md /root/feel/README.md 
ADD setup.py /root/feel/

# Install
RUN pip install -e /root/feel

# Run on startup
ENTRYPOINT [ "feel" ]