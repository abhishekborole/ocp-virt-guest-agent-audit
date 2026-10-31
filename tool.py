"""Collect live guest-agent connection conditions and guest interface data."""
import argparse
from decimal import Decimal
import json
import sys
import subprocess
from datetime import datetime, timezone
from oc_client import Client, VM, VMI, MIG, SNAP, quantity, age_hours, condition, require_name, stopped, escape, migration


def execute(client,args):
    return [{'name':v['metadata']['name'],'phase':v.get('status',{}).get('phase'),'agent':condition(v,'AgentConnected'),
             'interfaces':v.get('status',{}).get('interfaces',[]),'guest_os':v.get('status',{}).get('guestOSInfo',{})} for v in client.items(VMI)]


def main():
    parser = argparse.ArgumentParser(description='Collect live guest-agent connection conditions and guest interface data.')
    parser.add_argument('--context',required=True,help='Explicit existing oc kubeconfig context')
    parser.add_argument('--namespace',required=True,help='Namespace for workload operations')
    parser.add_argument('--name',help='Exact workload/resource name where required')
    parser.add_argument('--apply',action='store_true',help='Execute the requested change; default is preview')

    args = parser.parse_args()
    try:
        result = execute(Client(args.context,args.namespace),args)
        print(json.dumps({'context':args.context,'namespace':args.namespace,'collected_at':datetime.now(timezone.utc).isoformat(),'result':result},indent=2))
    except (RuntimeError,ValueError,KeyError,OSError,TimeoutError,subprocess.SubprocessError) as error:
        print(str(error),file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__': raise SystemExit(main())
