#!/bin/bash

#
# tally_vocabulary.sh – A script to count the occurrences of
#                       the different parts of speech


# show usage
[ $# -eq 0 ] && { echo "Usage: $0 vocab_file"; exit 1; }
[[ " $@ "  =~ " -h " ]] && { echo "Usage: $0 vocab_file"; exit 1; }

# check that file exists
FILE=$1
[ ! -f $FILE ] && { echo "Error: File $FILE not found"; exit 5; }

# find parts of speech labels
POS=$(cut -f2 $FILE | sort | uniq)

# count total and known POS words
TOTAL_COUNT=$(cat $FILE | wc -l)
UNKNOWN_COUNT=$(awk "/\tUNKNOWN\t/" $FILE | wc -l)
KNOWN_COUNT=$(echo "$TOTAL_COUNT - $UNKNOWN_COUNT" | bc -l)

# count and display occurrences
printf '%*s' 49 | tr ' ' '-'; echo
for label in $POS; do
    # count occurrences
    count=$(awk "/\t$label\t/" $FILE | wc -l)
    # calculate percent of known POS and right align
    if [ $label != "UNKNOWN" ]; then
        percent=$(printf %.1f $(echo "$count/$KNOWN_COUNT*100" | bc -l))
        if [ ${#percent} -lt 4 ]; then
            percent=" $percent"
        fi
    else
        percent="    "
    fi        
    # add thousands separator and right align result
    count=$(LC_NUMERIC=en_GB printf "%'d" $count)
    count=$(printf '%12s' $count | tr ',' ' ')
    # display results and pad label
    if [ ${#label} -lt 7 ]; then
        echo -e "|  $label\t\t\t| $count\t| $percent\t|"
    elif [ ${#label} -lt 11 ]; then
        echo -e "|  $label\t\t| $count\t| $percent\t|"
    else
        echo -e "|  $label\t| $count\t| $percent\t|"
    fi
done
printf '%*s' 49 | tr ' ' '-'; echo

# add thousands separator and display total count
TOTAL_COUNT=$(LC_NUMERIC=en_GB printf "%'d" $TOTAL_COUNT)
TOTAL_COUNT=$(printf '%12s' $TOTAL_COUNT | tr ',' ' ')
echo -e "|  TOTAL\t\t| $TOTAL_COUNT\t|     \t|"
printf '%*s' 49 | tr ' ' '-'; echo
