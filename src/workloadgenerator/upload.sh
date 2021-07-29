#!/bin/bash

# Adopted from https://gist.github.com/rtyler/30e51dc72bed23718388c43f9c11da76

# INPUT FILES
FILENAME=${1}
BLOB_NAME=${2}

echo "Uploading $FILENAME to $BLOB_NAME"

# expected to be defined in the environment
AZURE_STORAGE_ACCOUNT=$(echo $AZURE_STORAGE_CONNECTION_STRING | sed -r "s/(.+AccountName=)([^;]*)($|;.*)/\2/")
AZURE_ACCESS_KEY=$(echo $AZURE_STORAGE_CONNECTION_STRING | sed -r "s/(.*AccountKey=)([^;]*)($|;.*)/\2/")

# inspired by
# https://stackoverflow.com/questions/20103258/accessing-azure-blob-storage-using-bash-curl

authorization="SharedKey"

HTTP_METHOD="PUT"
request_date=$(TZ=GMT date "+%a, %d %h %Y %H:%M:%S %Z")
storage_service_version="2015-02-21"

# HTTP Request headers
x_ms_date_h="x-ms-date:$request_date"
x_ms_version_h="x-ms-version:$storage_service_version"
x_ms_blob_type_h="x-ms-blob-type:BlockBlob"

FILE_LENGTH=$(wc --bytes < ${FILENAME})
FILE_TYPE=$(file --mime-type -b ${FILENAME})
FILE_MD5=$(md5sum -b ${FILENAME} | awk '{ print $1 }')

# Build the signature string
canonicalized_headers="${x_ms_blob_type_h}\n${x_ms_date_h}\n${x_ms_version_h}"
canonicalized_resource="/${AZURE_STORAGE_ACCOUNT}/${AZURE_CONTAINER_NAME}/${BLOB_NAME}"

#######
# From: https://docs.microsoft.com/en-us/rest/api/storageservices/authentication-for-the-azure-storage-services
#
#StringToSign = VERB + "\n" +
#               Content-Encoding + "\n" +
#               Content-Language + "\n" +
#               Content-Length + "\n" +
#               Content-MD5 + "\n" +
#               Content-Type + "\n" +
#               Date + "\n" +
#               If-Modified-Since + "\n" +
#               If-Match + "\n" +
#               If-None-Match + "\n" +
#               If-Unmodified-Since + "\n" +
#               Range + "\n" +
#               CanonicalizedHeaders +
#               CanonicalizedResource;
string_to_sign="${HTTP_METHOD}\n\n\n${FILE_LENGTH}\n\n${FILE_TYPE}\n\n\n\n\n\n\n${canonicalized_headers}\n${canonicalized_resource}"

# Decode the Base64 encoded access key, convert to Hex.
decoded_hex_key="$(echo -n $AZURE_ACCESS_KEY | base64 -d -w0 | xxd -p -c256)"

# Create the HMAC signature for the Authorization header
signature=$(printf  "$string_to_sign" | openssl dgst -sha256 -mac HMAC -macopt "hexkey:$decoded_hex_key" -binary | base64 -w0)

authorization_header="Authorization: $authorization $AZURE_STORAGE_ACCOUNT:$signature"
OUTPUT_FILE="https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/${AZURE_CONTAINER_NAME}/${BLOB_NAME}"

HTTP_CODE=$(curl  \
    --write-out "%{http_code}\n" --silent \
    --output upload.log \
    -X ${HTTP_METHOD} \
    -T ${FILENAME} \
    -H "$x_ms_date_h" \
    -H "$x_ms_version_h" \
    -H "$x_ms_blob_type_h" \
    -H "$authorization_header" \
    -H "Content-Type: ${FILE_TYPE}" \
    ${OUTPUT_FILE})

if [ $HTTP_CODE -eq 201 ]; then
    # echo ${OUTPUT_FILE}
    exit 0;
fi;

cat upload.log
echo 
exit 1
