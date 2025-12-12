#!/bin/bash

echo Cleaning $1

if [ -z "$1" ]; then
    echo "No argument passed; expecting tmp/dtmc.prism"
    exit 1
fi

invalid_terms=("inc_p1_p1" "inc_p1_p3" "inc_p1_p4" "inc_p2_p1" "inc_p2_p2" "inc_p2_p4" "inc_p3_p1" "inc_p3_p2" "inc_p3_p3" "inc_p4_p1" "inc_p4_p2" "inc_p4_p3" "inc_p4_p4"\
               "dec_p1_p1" "dec_p1_p2" "dec_p1_p3" "dec_p1_p4" "dec_p2_p2" "dec_p2_p3" "dec_p2_p4" "dec_p3_p1" "dec_p3_p3" "dec_p3_p4" "dec_p4_p1" "dec_p4_p2" "dec_p4_p4" )

valid_terms=("inc_p1_p2" "inc_p2_p3" "inc_p3_p4" "dec_p4_p3" "dec_p3_p2" "dec_p2_p1")

for i in "${invalid_terms[@]}"; do
    sed "/[^!]${i}/d" "${1}" > "${1}.tmp"
    mv "${1}.tmp" "${1}"
    sed "s/\& \!${i}//g" "${1}" > "${1}.tmp"
    mv "${1}.tmp" "${1}"
done

for i in "${valid_terms[@]}"; do
    sed "/!${i}/d" "${1}" > "${1}.tmp"
    mv "${1}.tmp" "${1}"
    sed "s/\& ${i}//g" "${1}" > "${1}.tmp"
    mv "${1}.tmp" "${1}"
done

cat "${1}" | uniq > "${1}.tmp"
mv "${1}.tmp" "${1}"

echo "Done"

