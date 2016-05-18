from collections import OrderedDict
import json
import sys

def updateUserData(template, resource_name, script_path, vals):
    script = open(script_path).read()
    script = script % vals
    scriptList = template['Resources'][resource_name]['Properties']['UserData']['Fn::Base64']['Fn::Join'][1]
    lines = [x + '\n' for x in script.splitlines()]
    scriptList.extend(lines)

todo = [('LaunchConfig', 'user-data-app.sh'),
        ('DatabaseInstance', 'user-data-db.sh')]

vals = json.load(open(sys.argv[1], 'r'))
vals['env'] = sys.argv[2]

template = json.load(open('servers.json.template', 'r'), object_pairs_hook=OrderedDict)
for resource_name, script_path in todo:
    updateUserData(template, resource_name, script_path, vals)

print template
templateOut = open('servers.json', 'w')
templateOut.write(json.dumps(template, sort_keys=False, indent=4, separators=(',', ': ')))
templateOut.close()
