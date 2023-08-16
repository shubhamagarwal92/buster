# shellcheck disable=SC2162
read -p "Enter the base url you want to scrape (Default: docs.mila.quebec) " BASE_URL
read -p "Enter the name of the source (Default: sample_source) " SOURCE
# Default website
BASE_URL=${BASE_URL:-"https://docs.mila.quebec/"}
SOURCE=${SOURCE:-"sample_source"}

DOCS_DIR="$( echo "${BASE_URL}" | cut -d'/' -f3 | cut -d':' -f1)"

echo "Docs dir in: ${DOCS_DIR}"

CURRENT_TIME=$(date +"%T")
echo "Current time : $CURRENT_TIME"
export CURRENT_DIR=${PWD}

export RESOURCES_DIR="${CURRENT_DIR}"/"resources"
export CSV_FILE_PATH="${RESOURCES_DIR}"/"output.csv"
export VECTOR_STORE_PATH="deeplake_store"
#export VECTOR_STORE_PATH="${RESOURCES_DIR}"/"deeplake_store"

httrack "$BASE_URL" -O "${RESOURCES_DIR}"/docs_root_dir
# scrapy-1.0

python create_chunks.py \
--docs_dir "${DOCS_DIR}" \
--base_url "${BASE_URL}" \
--output_csv "${CSV_FILE_PATH}" \
--source "${SOURCE}"
#
#python generate_embeddings.py \
#--vector_store_path "${VECTOR_STORE_PATH}" \
#--csv_path "${CSV_FILE_PATH}" \
#
# gradio gradio_app.py