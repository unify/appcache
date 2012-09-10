#
# AppCache for Jasy - App cache supporting library
#
#
# Copyright (C) 2012 Sebastian Fastner, Mainz, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time, json


def getAssetManager(state):
	if hasattr(state, "assetManager"):
		return state.assetManager
	else:
		return state.session.getAssetManager()


def filenamesFromAsset(prefix, section, profiles, entries=None):
	if (entries == None):
		entries = []
	
	if section:
		for filename in section:
			entry = section[filename]
			if (len(prefix) > 0):
				id = prefix + "/" + filename
			else:
				id = filename
			
			if "p" in entry:
				entries.append(profiles[entry["p"]]["root"] + id)
			else:
				filenamesFromAsset(id, entry, profiles, entries)
		
	return entries
		

@share
def cacheManifest(state, scripts = ["script/application-%s.js"], htmlfile = "index.html", kernel = "script/kernel.js", ignoreAssets=False):
	timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
	appcache = """CACHE MANIFEST

# Jasy AppCache Manifest file
# Version: {version}

CACHE:
{htmlfile}
{kernel}
{scripts}
{assets}

NETWORK:
*"""

	htmlcache = '<!DOCTYPE html><html manifest="%s"></html>'

	# Create an application cache file for each permutation
	for permutation in state.session.permutate():
		if ignoreAssets:
			assets = []
		else:
			classes = state.Resolver().getIncludedClasses()
			assetConfig = json.loads(getAssetManager(state).export(classes))
			assets = filenamesFromAsset("", assetConfig["assets"], assetConfig["profiles"])
		
		# Set options
		checksum = permutation.getChecksum()
		
		scriptFiles = []
		for script in scripts:
			scriptFiles.append(script % checksum)
		
		manifestFilename = "appcache-%s.manifest" % (checksum)
		state.writeFile(manifestFilename, appcache.format(version=timestamp, htmlfile=htmlfile, kernel=kernel, scripts="\n".join(scriptFiles), assets="\n".join(assets)))
		
		state.writeFile("index-%s.html" % (checksum), htmlcache % (manifestFilename))

