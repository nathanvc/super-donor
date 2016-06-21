#! /usr/bin/env python
#'''//anaconda/bin/python'''
from dsr_app import app

#app.run(debug = True)

#!/usr/bin/env python
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
