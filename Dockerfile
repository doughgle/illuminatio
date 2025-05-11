FROM python:3.12-slim-bookworm AS builder

RUN mkdir -p /src/app && \
    apt-get update && \
    apt-get install -y git wget

ENV CRICTL_VERSION="v1.30.0"
RUN wget https://github.com/kubernetes-sigs/cri-tools/releases/download/${CRICTL_VERSION}/crictl-${CRICTL_VERSION}-linux-amd64.tar.gz && \
    tar zxvf crictl-${CRICTL_VERSION}-linux-amd64.tar.gz -C /usr/local/bin && \
    rm -f crictl-${CRICTL_VERSION}-linux-amd64.tar.gz

COPY setup.cfg /src/app
COPY setup.py /src/app
COPY .git /src/app/.git
COPY src /src/app/src
COPY ./requirements.txt /src/app/requirements.txt

WORKDIR /src/app
# First remove any standalone pathlib package that might conflict with Python 3.12's built-in pathlib
RUN pip3 --no-cache-dir uninstall -y pathlib || true
# Make sure we're using the latest pip
RUN pip3 --no-cache-dir install --upgrade pip
# Force reinstall urllib3 to fix compatibility issues
RUN pip3 --no-cache-dir install --force-reinstall urllib3==2.0.7
# Now install requirements and the package
RUN pip3 --no-cache-dir install -r ./requirements.txt
RUN pip3 --no-cache-dir install --no-deps .

# Actual Runner image
FROM python:3.12-slim-bookworm

# Install illuminatio from builder
COPY --from=builder /src/app/src /src/app/src
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/illuminatio-runner /usr/local/bin/illuminatio-runner
COPY --from=builder /usr/local/bin/illuminatio /usr/local/bin/illuminatio
COPY --from=builder /usr/local/bin/crictl /usr/local/bin/crictl

# Clean up any pathlib package in the final image to avoid conflicts
RUN rm -f /usr/local/lib/python3.12/site-packages/pathlib.py
RUN rm -f /usr/local/lib/python3.12/site-packages/pathlib.pyc

ENV PYTHONPATH=/usr/local/lib/python3.12/site-packages
# Home directory of root user is not recognized when using ~ (default: ~/.kube/config)
ENV KUBECONFIG=/kubeconfig

# Currently nmap is required for running the scans
RUN apt-get update && \
    apt-get install -y nmap && \
    rm -rf /var/lib/apt/lists/*

CMD [ "/usr/local/bin/illuminatio-runner" ]
