virtualenv -p /usr/bin/python3 venv/
source venv/bin/activate
python -m pip install -r requirements.txt
pip install --editable .
graft_netem --help