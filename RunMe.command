#!/bin/bash
cd "$(dirname "$0")";
bokeh serve --show maincode.py ;
exit;