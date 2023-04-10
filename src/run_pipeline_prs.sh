#!/bin/sh

projects=(
 'https://github.com/streamlit/streamlit'
 'https://github.com/has2k1/plotnine'
 'https://github.com/pydantic/pydantic'
 'https://github.com/tidyverse/ggplot2'
 'https://github.com/tidyverse/dplyr'
 'https://github.com/pandas-dev/pandas'
 'https://github.com/tiangolo/fastapi'
 'https://github.com/sqlalchemy/sqlalchemy'
 'https://github.com/tidyverse/lubridate'
)

for proj in "${projects[@]}";
do
    echo "Checking the $proj url new merged PRs"
    the_project_tracker -u $proj prs -n 10 --code_diff

done
