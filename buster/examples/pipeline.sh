# shellcheck disable=SC2162
# Taking input from the users
read -p "Do you want to scrape website using httrack (1 - Yes, 0 - no), default 1: " DO_HTTRACK
read -p "Enter the base url you want to scrape (Default: https://docs.mila.quebec/) " BASE_URL
read -p "Enter the name of the source (Default: sample_source) " SOURCE
read -p "Do you want to create chunks (1 - Yes, 0 - no), default 1: " DO_CHUNKS
read -p "Do you want to create embeddings (1 - Yes, 0 - no), default 1: " DO_EMBED
read -p "Do you want to launch gradio app (1 - Yes, 0 - no), default 1: " DO_GRADIO


# Default values
BASE_URL=${BASE_URL:-"https://docs.mila.quebec/"}
SOURCE=${SOURCE:-"sample_source"}
DO_CHUNKS=${DO_CHUNKS:-1}
DO_HTTRACK=${DO_HTTRACK:-1}
DO_EMBED=${DO_EMBED:-1}
DO_GRADIO=${DO_GRADIO:-1}

# Current time
CURRENT_TIME=$(date +"%T")
echo "Current time : $CURRENT_TIME"
export CURRENT_DIR=${PWD}

# Export paths
export RESOURCES_DIR="${CURRENT_DIR}"/"resources"
export CSV_FILE_PATH="${RESOURCES_DIR}"/"output.csv"
export VECTOR_STORE_PATH="deeplake_store"
# TODO make deepstore generic
#export VECTOR_STORE_PATH="${RESOURCES_DIR}"/"deeplake_store"
export DOCS_ROOT_DIR="${RESOURCES_DIR}"/"docs_root_dir"
# Get the dir name from base url
DOCS_TO_PARSE_DIR=$( echo "${BASE_URL}" | cut -d'/' -f3 | cut -d':' -f1)
export DOCS_DIR="${DOCS_ROOT_DIR}"/"${DOCS_TO_PARSE_DIR}"
echo "Docs are parsed in only directory: ${DOCS_DIR}"

if [ "${DO_HTTRACK}" == 1 ]; then
httrack "$BASE_URL" -O "${RESOURCES_DIR}"/docs_root_dir
# scrapy-1.0
echo "Website scraped"
fi


if [ "${DO_CHUNKS}" == 1 ]; then
python create_chunks.py \
--docs_dir "${DOCS_DIR}" \
--base_url "${BASE_URL}" \
--output_csv "${CSV_FILE_PATH}" \
--source "${SOURCE}" \
--filter
echo "Chunks created"
fi


if [ "${DO_EMBED}" == 1 ]; then
python generate_embeddings.py \
--vector_store_path "${VECTOR_STORE_PATH}" \
--csv_path "${CSV_FILE_PATH}"
echo "Embeddings created"
fi



if [ "${DO_GRADIO}" == 1 ]; then
gradio gradio_app.py
echo "App launched"
fi
