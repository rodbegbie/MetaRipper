#!/usr/bin/python
import os
from Util import walk

for root, dirs, files in walk("/mnt/flac"):
	if not os.path.exists(os.path.join(root, 'cover.jpg')):
		if (os.path.split(root))[0] <> '/mnt/flac':
			print root
