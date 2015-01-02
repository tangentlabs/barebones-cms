#!/bin/bash

OUTPUT=`psql -lt | grep cms_vagrant | wc -l`

if [ "$OUTPUT" -eq 0 ]
then
  psql -c "UPDATE pg_database SET datistemplate = FALSE where datname = 'template1'"; psql -c "DROP database template1";
  echo "Dropped template";
else
  echo "Kept Template";
fi
