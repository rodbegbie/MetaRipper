#!/usr/bin/python
import os
from Util import walk

for root, dirs, files in walk("/mnt/mp3/non-flac/mbtagged"):#flac"):
	if not os.path.exists(os.path.join(root, 'cover.jpg')):
		if (os.path.split(root))[0] <> '/mnt/mp3/non-flac/mbtagged':
			print root
