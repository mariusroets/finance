### Multi-stage image creation
### The conda files for eskom packages are in the orabase image. Get it from there
FROM debian:buster-slim AS runtime
### Use the miniconda image as a base to create the development environment
FROM continuumio/miniconda3:latest AS build
WORKDIR /app
RUN conda update conda
RUN conda config --add channels conda-forge
RUN conda update --all
COPY *.yml ./
# This creates the development environment
RUN conda env create --file finance.yml
# Now, pack and unpack the environment
RUN conda install conda-pack
RUN conda-pack -n finance -o /tmp/env.tar && mkdir /opt/finance && cd /opt/finance && tar -xf /tmp/env.tar && rm /tmp/env.tar
RUN /opt/finance/bin/conda-unpack

FROM runtime
# Only copy the environment from the build image
EXPOSE 5000/tcp
COPY --from=build /opt/finance /opt/finance
WORKDIR /app
COPY install_deps.sh /app/
RUN chmod +x /app/install_deps.sh
RUN /app/install_deps.sh
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
