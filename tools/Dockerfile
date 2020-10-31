FROM python:3.9.0-alpine3.12

LABEL name="StreamHelper"
LABEL version="0.1.0"
LABEL source="https://github.com/VisionTale/StreamHelper"

ARG DEBUG=0
ARG MODE='production'
ARG PORT=5000

ARG BASEDIR
ARG WORKDIR
ARG SH_CONFIG_DIR
ARG SH_CACHE_DIR
ARG SH_DATA_DIR
ARG DATABASE_URL
ARG SH_TEMPLATE_PATH
ARG SH_STATIC_PATH
ARG SH_PLUGIN_PATH
ARG SH_MACRO_PATH
ARG SH_LOG_TYPES
ARG SH_LOG_LEVEL

ENV BASEDIR=${BASEDIR:-'/srv'}
ENV WORKDIR=${WORKDIR:-"$BASEDIR/app"}
ENV SH_CONFIG_DIR=${SH_CONFIG_DIR:-"$BASEDIR/config"}
ENV SH_CACHE_DIR=${SH_CACHE_DIR:-"$BASEDIR/cache"}
ENV SH_DATA_DIR=${SH_DATA_DIR:-"$BASEDIR/data"}
ENV DATABASE_URL=${DATABASE_URL:-"sqlite://$SH_CONFIG_DIR/streamhelper.db"}
ENV SH_TEMPLATE_PATH=${SH_TEMPLATE_PATH:-"$SH_DATA_DIR/templates"}
ENV SH_STATIC_PATH=${SH_STATIC_PATH:-"$SH_DATA_DIR/static"}
ENV SH_PLUGIN_PATH=${SH_PLUGIN_PATH:-"$SH_DATA_DIR/blueprints"}
ENV SH_MACRO_PATH=${SH_MACRO_PATH:-"$SH_DATA_DIR/macros"}
ENV SH_LOG_TYPES=${SH_LOG_TYPES:-'STREAM'}
ENV SH_LOG_LEVEL=${SH_LOG_LEVEL:-'WARNING'}

RUN apk add --no-cache sqlite

RUN mkdir -p "$BASEDIR" "$WORKDIR" "$SH_CONFIG_DIR" "$SH_CACHE_DIR" "$SH_DATA_DIR" \
"$SH_TEMPLATE_PATH" "$SH_STATIC_PATH" "$SH_PLUGIN_PATH" "$SH_MACRO_PATH"

WORKDIR "$WORKDIR"

RUN printf "export FLASK_APP=webapi.py\n\
export FLASK_DEBUG=$DEBUG\n\
export FLASK_ENV=$MODE\n\
export FLASK_RUN_HOST = 0.0.0.0\n\
export FLASK_RUN_PORT = $PORT\n\
"\
>> "$WORKDIR/.flaskenv"

COPY ../webapi.py "$WORKDIR/"
COPY ../start.sh "$WORKDIR/"
COPY ../webapi "$WORKDIR/webapi"
COPY ../requirements.txt "$WORKDIR/"
COPY ../migrations "$WORKDIR/migrations"
COPY tools "$WORKDIR/tools"
COPY ../templates "$SH_TEMPLATE_PATH/"
COPY ../static "$SH_STATIC_PATH/"
COPY ../webapi/blueprints "$SH_PLUGIN_PATH/"
COPY ../webapi/macros "$SH_MACRO_PATH/"

RUN python3 -m pip install --upgrade pip wheel virtualenv
VOLUME "$BASEDIR"/venv

RUN python3 "$WORKDIR/webapi/libs/config.py"

EXPOSE $PORT

VOLUME $SH_CONFIG_DIR

ENTRYPOINT ["/bin/sh", "start.sh"]

HEALTHCHECK --interval=5m --timeout=15s \
  CMD python3 "$WORKDIR/tools/healthcheck.py" || exit 1