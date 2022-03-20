import subprocess
import collections
from config import PARTITION_CHAIN_PREFIX, DOCKER_USER_CHAIN

def parse_partition_index(partition_chain):
    if partition_chain.startswith(PARTITION_CHAIN_PREFIX):
        return int(partition_chain[len(PARTITION_CHAIN_PREFIX):])
    else:
        raise ValueError("parse_partition_index error")

class IPTables(object):

    def __init__(self) -> None:
        pass

    def call_output(self, *args):
        cmd = ["sudo", "iptables", "-n"] + list(args)
        output = subprocess.run(cmd, capture_output=True, text=True).stdout
        return output.split('\n')

    def call(self, *args):
        cmd = ["sudo", "iptables"] + list(args)
        return subprocess.run(cmd)

    def get_chain_rules(self, chain):
        if not chain:
            raise ValueError("invalid chain")
        lines = self.call_output("-L", chain)
        if len(lines) < 2:
            raise ValueError("Can't understand iptables output: \n%s" %
                                "\n".join(lines))

        chain_line, header_line = lines[:2]
        if not (chain_line.startswith("Chain " + chain) and
                header_line.startswith("target")):
            raise ValueError("Can't understand iptables output: \n%s" %
                                "\n".join(lines))
        return lines[2:]

    def get_source_chains(self):
        result = {}
        lines = self.get_chain_rules(DOCKER_USER_CHAIN)

        for line in lines:
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                parse_partition_index(parts[0])
            except ValueError:
                continue  # not a rule targetting a partition chain

            source = parts[3]
            if source:
                result[source] = parts[0]
        return result

    def delete_rules(self, chain, predicate):
        if not chain:
            raise ValueError("invalid chain")
        if not isinstance(predicate, collections.Callable):
            raise ValueError("invalid predicate")

        lines = self.get_chain_rules(chain)

        for index, line in reversed(list(enumerate(lines, 1))):
            line = line.strip()
            if line and predicate(line):
                self.call("-D", chain, str(index))

    def delete_partition_rules(self):
        def predicate(rule):
            target = rule.split()[0]
            try:
                parse_partition_index(target)
            except ValueError:
                return False
            return True
        self.delete_rules(DOCKER_USER_CHAIN, predicate)

    def delete_partition_chains(self):
        lines = self.call_output("-L")
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[0] == "Chain":
                chain = parts[1]
                try:
                    parse_partition_index(chain)
                except ValueError:
                    continue
                # if we are a valid blockade chain, flush and delete
                self.call("-F", chain)
                self.call("-X", chain)

    def insert_rule(self, chain, src=None, dest=None, target=None):
        """Insert a new rule in the chain
        """
        if not chain:
            raise ValueError("Invalid chain")
        if not target:
            raise ValueError("Invalid target")
        if not (src or dest):
            raise ValueError("Need src, dest, or both")

        args = ["-I", chain]
        if src:
            args += ["-s", src]
        if dest:
            args += ["-d", dest]
        args += ["-j", target]
        self.call(*args)

    def create_chain(self, chain):
        """Create a new chain
        """
        if not chain:
            raise ValueError("Invalid chain")
        self.call("-N", chain)

    def clear(self):
        """Remove all iptables rules and chains related to this blockade
        """
        # first remove refererences to our custom chains
        self.delete_partition_rules()

        # then remove the chains themselves
        self.delete_partition_chains()
