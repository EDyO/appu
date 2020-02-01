DROPBOX_CLI=${HOME}/bin/dropbox.py
PROJECTS_PATH=${HOME}/src
DRIVE_CREDENTIALS_FILE=../.credentials/edyo-test-5159ae711f8b.json
PUBLIC_FEED=http://podcast.edyo.es/feed_podcast.xml

function count_tracks {
  curl -s ${PUBLIC_FEED} > /tmp/feedpodcast.xml
  goxpath -u '/rss/channel/item' /tmp/feedpodcast.xml | wc -l
}

function get_episode_script {
  echo "Obteniendo el guión para ${1}" >&2
  SCRIPT_NAME_HOOK=$(
    echo ${1} | \
    awk -F. '{ print $1 }' | \
    tr '-' ' ' | \
    sed -e 's/edyo pildora/Píldora /' \
        -e 's/edyo colaboracion /Colaboracion /' \
        -e 's/edyo/Podcast/'
  )
  echo "Buscando el guión ${SCRIPT_NAME_HOOK}" >&2
  SCRIPT_DATA=$(
    gdrive --service-account ${DRIVE_CREDENTIALS_FILE} list \
           --no-header \
           --query "name contains '${SCRIPT_NAME_HOOK}'" | \
    tr -s ' ' | \
    sed -e 's/^\([-_0-9a-zA-Z]*\) \(.*\) doc \(.*\)$/\1;\2;\3/'
  )
  if [[ "$?" != "0" ]]; then
    echo "Fallo buscando el guión" >&2
    exit 1
  fi
  echo "Descargando el guión ${SCRIPT_NAME_HOOK}" >&2
  SCRIPT_ID=$(echo ${SCRIPT_DATA} | cut -d\; -f1)
  EXPORT_OUTPUT=$(
    gdrive --service-account ${DRIVE_CREDENTIALS_FILE} export \
           --mime text/html ${SCRIPT_ID}
  )
  if [[ "$?" != "0" ]]; then
    echo -e "\nFallo exportando el guión" >&2
    exit 1
  fi
  EXPORT_FILE=$(
    echo ${EXPORT_OUTPUT} | \
    sed -e "s/Exported '\(.*\)' with.*$/\1/" -e "s/ /\\ /g"
  )
  mv "${EXPORT_FILE}" /tmp/${1}_script.html
  echo "${SCRIPT_DATA};/tmp/${1}_script.html"
}

function get_dropbox_url {
  echo "Obteniendo URL del episodio" >&2
  OUTPUT=$(${DROPBOX_CLI} sharelink ${1} | sed -e 's/dl=0/dl=1/')
  if [[ "${OUTPUT}" =~ ^https:.*?dl=1$ ]]; then
    echo ${OUTPUT} | sed -e 's/?dl=1/?dl=0/g'
  else
    echo ${OUTPUT} >&2
    exit 1
  fi
}

function clone_appu {
  curdir=$(pwd)
  if [[ ! -d ${PROJECTS_PATH}/appu/.git ]]; then
    echo "Clonando appu" >&2
    cd ${PROJECTS_PATH}
    git clone git@github.com:EDyO/appu >&2 || exit 1
  else
    echo "Actualizando appu" >&2
    cd ${PROJECTS_PATH}/appu
    git checkout master >&2 || exit 1
    git pull >&2 || exit 1
  fi
  cd ${curdir}
}

function get_episode_details {
  echo "Obteniendo detalles del episodio" >&2
  MASTER_FILE_NAME=$(
    echo ${1} | \
    awk -F/ '{ print $NF }'
  )
  export FINAL_FILE_NAME=$(
    echo ${MASTER_FILE_NAME} | \
    sed -e 's/.master//g'
  )
  SCRIPT_DATA=$(get_episode_script ${MASTER_FILE_NAME})
  if [[ "$?" != 0 ]]; then
    exit 1
  fi
  echo "Procesando el guión para obtener detalles" >&2
  SCRIPT_NAME=$(echo ${SCRIPT_DATA} | cut -d\; -f2)
  SCRIPT_DATE=$(echo ${SCRIPT_DATA} | cut -d\; -f3)
  EPISODE_SCRIPT=$(echo ${SCRIPT_DATA} | cut -d\; -f4)
  echo -n "Obteniendo título " >&2
  export EPISODE_TITLE=$(
    echo ${SCRIPT_NAME} | \
    sed -e 's/^Podcast/EDyO/' \
        -e 's/^Píldora/EDyO &/' \
        -e 's/^Colaboración/EDyO &/'
  )
  echo ${EPISODE_TITLE} >&2
  echo -n "Obteniendo año " >&2
  export EPISODE_YEAR=$(echo ${SCRIPT_DATE} | cut -d- -f1)
  echo ${EPISODE_YEAR} >&2
  echo -n "Obteniendo pista " >&2
  export EPISODE_TRACK=$(($(count_tracks) + 1))
  echo ${EPISODE_TRACK} >&2
  echo -n "Obteniendo comentario " >&2
  export EPISODE_COMMENT=$(
    goxpath -u -v '/html/body/p[contains(@style,"color:#666666;")]' \
      ${EPISODE_SCRIPT} | recode html..utf-8
  )
  echo ${EPISODE_COMMENT} >&2
  echo "Obteniendo enlaces" >&2
  export EPISODE_LINKS=""
  LI=1
  XPATH="/html/body/ul[last()]/li"
  LINK=$(
    goxpath -u -v "${XPATH}[${LI}]" ${EPISODE_SCRIPT} | \
    recode html..utf-8
  )
  while [[ "${LINK}" != "" ]]; do
    echo -e "\t${LINK}" >&2
    export EPISODE_LINKS="${EPISODE_LINKS}#${LINK}"
    LI=$((${LI} + 1))
    LINK=$(
      goxpath -u -v "${XPATH}[${LI}]" ${EPISODE_SCRIPT} | \
      recode html..utf-8
    )
  done
  export APPU_OUTPUT_FILE_NAME=podcast/$(
    echo ${FINAL_FILE_NAME} | \
    awk -F. '{ print $1 }'
         ).mp3
}

function run_appu {
  echo "Configurando ejecución de appu" >&2
  envsubst < templates/appu.cfg >${PROJECTS_PATH}/appu/config.cfg
  cd ${PROJECTS_PATH}/appu
  git add config.cfg >&2
  git commit -m "Track ${EPISODE_TRACK} " >&2
  COMMIT_ID=$(git rev-parse HEAD)
  git push >&2 || exit 1
  echo -n "Ejecutando appu" >&2
  TRAVIS_BLDS_URL=https://api.travis-ci.org/repos/EDyO/appu/builds
  JQ_QUERY=". as { builds: \$builds, commits: \$commits} | \$builds[] |"
  JQ_QUERY="${JQ_QUERY} select(.commit_id == (\$commits[] |"
  JQ_QUERY="${JQ_QUERY} select(.sha == env.COMMIT_ID).id)).state"
  BLD_STATE=$(
    curl -s -H 'Accept:application/vnd.travis-ci.2+json' \
      -G ${TRAVIS_BLDS_URL} | \
    COMMIT_ID=${COMMIT_ID} jq "${JQ_QUERY}" | \
    tr -d '"'
  )
  while [[ "${BLD_STATE}" != "passed" && "${BLD_STATE}" != "failed" ]]; do
    echo -n "." >&2
    sleep 30
    BLD_STATE=$(
      curl -s -H 'Accept:application/vnd.travis-ci.2+json' \
        -G ${TRAVIS_BLDS_URL} | \
      COMMIT_ID=${COMMIT_ID} jq "${JQ_QUERY}" | \
      tr -d '"'
    )
  done
  echo ${BLD_STATE}
  cd - > /dev/null
}

function ssh_server {
  ssh edyo@podcast.edyo.es "${1}"
}

function download_edited_mp3 {
  echo "Descargando el episodio editado en el servidor" >&2
  EPISODE_URL="https://github.com/EDyO/appu/raw/travis_ci/"
  EPISODE_URL="${EPISODE_URL}${APPU_OUTPUT_FILE_NAME}"
  export EPISODE_LENGTH=$(
    curl -sL -I ${EPISODE_URL} | \
    grep 'Content-Length' | \
    awk '{ print $2 }'
  )
  EPISODE_DEST="podcast/files/${FINAL_FILE_NAME}"
  curl -sLG ${EPISODE_URL} > /tmp/${FINAL_FILE_NAME}
  scp /tmp/${FINAL_FILE_NAME} edyo@podcast.edyo.es:${EPISODE_DEST}
  rm /tmp/${FINAL_FILE_NAME}
}

function update_feed {
  echo "Actualizando el feed" >&2
  I='    '
  ssh_server "echo -ne '${I}- title: ${EPISODE_TITLE}\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}  description: |\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}    ${EPISODE_COMMENT}\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}    Blog EntreDevYOps - http://www.entredevyops.es\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}    Twitter EntreDevYOps - https://twitter.com/EntreDevYOps\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}    LinkedIn EntreDevYOps - https://www.linkedin.com/in/entre-dev-y-ops-a7404385/\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}    Patreon EntreDevYOps - https://www.patreon.com/edyo\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}    Amazon EntreDevYOps - https://amzn.to/2HrlmRw\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}    Enlaces comentados:' >> feed_podcast.yml"
  LINKS=$(echo ${EPISODE_LINKS} | sed -e 's/#/\\n        /g')
  ssh_server "echo -ne '${I}    ${LINKS}\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}  link: http://podcast.edyo.es/${APPU_OUTPUT_FILE_NAME}\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}  pubDate: $(TZ='UTC' date -R)\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}  enclosure:\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}    attributes:\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}      length: ${EPISODE_LENGTH}\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}      type: audio/mpeg\n' >> feed_podcast.yml"
  ssh_server "echo -ne '${I}      url: http://podcast.edyo.es/${APPU_OUTPUT_FILE_NAME}\n' >> feed_podcast.yml"
  ssh_server "./pan feed_podcast.yml > podcast/feed_podcast.xml"
}

function validate_publishing {
  echo "Validando feed" >&2
  VALIDATION_URL="https://validator.w3.org/feed/check.cgi?"
  VALIDATION_URL="${VALIDATION_URL}url=podcast.edyo.es%2Ffeed_podcast.xml"
  curl -s ${VALIDATION_URL} | \
  egrep -c "This feed does not validate|This feed is valid, but"
}

function check_publishing {
  URL=${1:-"http://feedpress.me/edyo"}
  FEED=${2:-"FeedPress"}
  echo -n "Comprobando publicación en ${FEED}" >&2
  PRESENCE=$(
    curl -s ${URL} | \
    grep -c "${EPISODE_TITLE}"
  )
  while [[ "${PRESENCE}" == "0" ]]; do
    sleep 60
    echo -n "."
    PRESENCE=$(
      curl -s ${URL} | \
      grep -c "${EPISODE_TITLE}"
    )
  done
  echo " Ya está en ${FEED}" >&2
}

function check_publishing_all {
  check_publishing
  IVOOX_URL="https://www.ivoox.com/"
  IVOOX_URL="${IVOOX_URL}podcast-entre-dev-y-ops-podcast_sq_f1112910_1"
  IVOOX_URL="${IVOOX_URL}.html"
  check_publishing ${IVOOX_URL} iVoox
  ITUNES_URL="https://itunes.apple.com/es/podcast/entredevyops-podcast/"
  ITUNES_URL="${ITUNES_URL}id866788492?mt=2"
  check_publishing ${ITUNES_URL} iTunes
}

if [[ "${1}" == "" ]]; then
  echo "No se ha especificado fichero de la grabación" >&2
  exit 1
fi
RECORDING=${1}

export RECORDING_URL=$(get_dropbox_url ${RECORDING})
if [[ "$?" == "0" ]]; then
  clone_appu || exit 1
  get_episode_details ${RECORDING} || exit 1
  APPU_JOB_RESULT=$(run_appu)
  if [[ "${APPU_JOB_RESULT}" == "passed" ]]; then
    download_edited_mp3 || exit 1
    update_feed || exit 1
    VALIDATION_ERRORS=$(validate_publishing)
    if [[ "${VALIDATION_ERRORS}" == "0" ]]; then
      check_publishing_all || exit 1
    else
      echo "El RSS no valida"
    fi
  else
    echo "El build de Appu falló" >&2
    exit 1
  fi
fi
