#!/bin/sh

projects=(
 'https://github.com/pola-rs/polars'
 'https://github.com/boto/boto3'
 'https://github.com/pytorch/pytorch'
 'https://github.com/tensorflow/tensorflow'
 'https://github.com/public-apis/public-apis'
 'https://github.com/huggingface/diffusers'
 'https://github.com/huggingface/transformers'
 'https://github.com/scikit-learn/scikit-learn'
 'https://github.com/pytest-dev/pytest'
 'https://github.com/keras-team/keras'
 'https://github.com/python-poetry/poetry'
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
    the_project_tracker -u $proj prs -n 5 --code_diff

done
