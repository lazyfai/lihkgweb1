#!/usr/bin/env python
import os
import sys
import newrelic.agent
newrelic.agent.initialize()

sys.path.insert(0, os.path.dirname(__file__) or '.')
PY_DIR = os.path.join(os.environ['OPENSHIFT_HOMEDIR'], "python")
from flaskapp import app as application
