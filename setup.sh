mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
 --server.port 8888
\n\
" > ~/.streamlit/config.toml